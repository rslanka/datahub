import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Iterable, List, Optional, Type, TypeVar, cast

import pydantic

from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.ingestion.api.ingestion_job_state_provider import JobId
from datahub.ingestion.api.workunit import MetadataWorkUnit
from datahub.ingestion.source.state.checkpoint import Checkpoint, CheckpointStateBase
from datahub.ingestion.source.state.stateful_ingestion_base import (
    StatefulIngestionConfig,
    StatefulIngestionReport,
    StatefulIngestionSourceBase,
)
from datahub.metadata.schema_classes import ChangeTypeClass, StatusClass

logger: logging.Logger = logging.getLogger(__name__)


class StatefulStaleMetadataRemovalConfig(StatefulIngestionConfig):
    """
    Base specialized config for Stateful Ingestion with stale metadata removal capability.
    """

    _entity_types: List[str] = []
    remove_stale_metadata: bool = pydantic.Field(
        default=True,
        description=f"Soft-deletes the entities of type {', '.join(_entity_types)} in the last successful run but missing in the current run with stateful_ingestion enabled.",
    )


@dataclass
class StaleEntityRemovalSourceReport(StatefulIngestionReport):
    soft_deleted_stale_entities: List[str] = field(default_factory=list)

    def report_stale_entity_soft_deleted(self, urn: str) -> None:
        self.soft_deleted_stale_entities.append(urn)


Derived = TypeVar("Derived")


class StaleEntityCheckpointStateBase(CheckpointStateBase, ABC, Generic[Derived]):
    """
    Defines the abstract interface for the checkpoint states that are used for stale entity removal.
    Examples include sql_common state for tracking table and & view urns,
    dbt that tracks node & assertion urns, kafka state tracking topic urns.
    """

    @classmethod
    @abstractmethod
    def get_supported_types(cls) -> List[str]:
        pass

    @abstractmethod
    def add_checkpoint_urn(self, type: str, urn: str) -> None:
        """
        Adds an urn into the list used for tracking the type.
        :param type: The type of the urn such as a 'table', 'view',
         'node', 'topic', 'assertion' that the concrete sub-class understands.
        :param urn: The urn string
        :return: None.
        """
        pass

    @abstractmethod
    def get_urns_not_in(self, type: str, other_checkpoint: "Derived") -> Iterable[str]:
        """
        Gets the urns present in this checkpoint but not the other_checkpoint for the given type.
        :param type: The type of the urn such as a 'table', 'view',
         'node', 'topic', 'assertion' that the concrete sub-class understands.
        :param other_checkpoint: the checkpoint to compute the urn set difference against.
        :return: an iterable to the set of urns present in this checkpoing state but not in the other_checkpoint.
        """
        pass


class StaleEntityRemovalHandler:
    """
    The stateful ingestion helper class that handles stale entity removal.
    This contains the generic logic for all sources that need to support stale entity removal for all the states
    derived from StaleEntityCheckpointStateBase. This uses the template method pattern on CRTP based derived state
    class hierarchies.
    """

    def __init__(
        self,
        source: StatefulIngestionSourceBase,
        config: Optional[StatefulStaleMetadataRemovalConfig],
        state_type_class: Type[StaleEntityCheckpointStateBase],
        job_id: JobId,
        pipeline_name: Optional[str],
        run_id: str,
    ):
        self.config = config
        self.source = source
        self.state_type_class = state_type_class
        self.job_id = job_id
        self.pipeline_name = pipeline_name
        self.run_id = run_id
        self.is_checkpointing_enabled = (
            source.is_stateful_ingestion_configured()
            and config
            and config.remove_stale_metadata
        )

    def _ignore_old_state(self) -> bool:
        if (
            self.is_checkpointing_enabled
            and self.config is not None
            and self.config.ignore_old_state
        ):
            return True
        return False

    def _ignore_new_state(self) -> bool:
        if (
            self.is_checkpointing_enabled
            and self.config is not None
            and self.config.ignore_new_state
        ):
            return True
        return False

    def create_checkpoint(self) -> Optional[Checkpoint]:
        if self._ignore_new_state():
            return None
        assert self.config is not None
        assert self.pipeline_name is not None
        return Checkpoint(
            job_name=self.job_id,
            pipeline_name=self.pipeline_name,
            platform_instance_id=self.source.get_platform_instance_id(),
            run_id=self.run_id,
            config=self.config,
            state=self.state_type_class(),
        )

    def _create_soft_delete_workunit(self, urn: str, type: str) -> MetadataWorkUnit:

        logger.info(f"Soft-deleting stale entity of type {type} - {urn}.")
        mcp = MetadataChangeProposalWrapper(
            entityType=type,
            entityUrn=urn,
            changeType=ChangeTypeClass.UPSERT,
            aspectName="status",
            aspect=StatusClass(removed=True),
        )
        wu = MetadataWorkUnit(id=f"soft-delete-{type}-{urn}", mcp=mcp)
        report = self.source.get_report()
        assert isinstance(report, StaleEntityRemovalSourceReport)
        report.report_workunit(wu)
        report.report_stale_entity_soft_deleted(urn)
        return wu

    def gen_removed_entity_workunits(self) -> Iterable[MetadataWorkUnit]:
        if self._ignore_old_state():
            return
        logger.debug("Checking for stale entity removal.")
        last_checkpoint: Optional[Checkpoint] = self.source.get_last_checkpoint(
            self.job_id, self.state_type_class
        )
        if not last_checkpoint:
            return
        cur_checkpoint = self.source.get_current_checkpoint(self.job_id)
        assert cur_checkpoint is not None
        # Get the underlying states
        last_checkpoint_state = cast(
            StaleEntityCheckpointStateBase, last_checkpoint.state
        )
        cur_checkpoint_state = cast(
            StaleEntityCheckpointStateBase, cur_checkpoint.state
        )
        for type in self.state_type_class.get_supported_types():
            for urn in last_checkpoint_state.get_urns_not_in(
                type=type, other_checkpoint=cur_checkpoint_state
            ):
                yield self._create_soft_delete_workunit(urn, type)

    def add_entity_to_state(self, type: str, urn: str) -> None:
        if self._ignore_new_state():
            return
        cur_checkpoint = self.source.get_current_checkpoint(self.job_id)
        assert cur_checkpoint is not None
        cur_state = cast(StaleEntityCheckpointStateBase, cur_checkpoint.state)
        cur_state.add_checkpoint_urn(type=type, urn=urn)
