import FeatureAvailability from '@site/src/components/FeatureAvailability';

# About DataHub Column Lineage
Column lineage captures the set of columns(upstream) a given dataset column(downstream) is derived from. 
This is also referred to as field-level lineage or fine-grained lineage. While capturing the column-lineage 
in this pure form is very appealing(typically achieved by parsing SQL), some SQL dialects allow for operators such as the bash operator 
and custom-transformations that can execute arbitrary external code which makes reasoning about individual column lineage very hard leading to
another kind of column-lineage which is from a set of downstream columns to a set of upstream columns. Not just that,
even when such approximate lineage is derived, we can't be 100% sure about it depending on the SQL operator and the
heuristics used in the SQL parse tools.
Datahub allows for representing both these forms of column-lineage via [FineGrainedLineage](https://github.com/datahub-project/datahub/blob/master/metadata-models/src/main/pegasus/com/linkedin/dataset/FineGrainedLineage.pdl) model. 

<!-- All Feature Guides should begin with `About DataHub ` to improve SEO -->

<!-- 
Update feature availability; by default, feature availabilty is Self-Hosted and Managed DataHub
Add in `saasOnly` for Managed DataHub-only features
 -->

<FeatureAvailability/>

<!-- This section should provide a plain-language overview of feature. Consider the following:
* What does this feature do? Why is it useful?
* What are the typical use cases?
* Who are the typical users?
* In which DataHub Version did this become available? -->

## Column Lineage Setup, Prerequisites, and Permissions

<!-- This section should provide plain-language instructions on how to configure the feature:
* What special configuration is required, if any?
* How can you confirm you configured it correctly? What is the expected behavior?
* What access levels/permissions are required within DataHub? -->

## Using Column Lineage

<!-- Plain-language instructions of how to use the feature
Provide a step-by-step guide to use feature, including relevant screenshots and/or GIFs
* Where/how do you access it?
* What best practices exist?
* What are common code snippets?
 -->

## Additional Resources

<!-- Comment out any irrelevant or empty sections -->

### Videos

<!-- Use the following format to embed YouTube videos:
**Title of YouTube video in bold text**
<p align="center">
<iframe width="560" height="315" src="www.youtube.com/embed/VIDEO_ID" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</p> 
-->

<!-- 
NOTE: Find the iframe details in YouTube by going to Share > Embed 
 -->

### API
#### GraphQL

<!-- Bulleted list of relevant GraphQL docs; comment out section if none -->

### DataHub Blog

<!-- Bulleted list of relevant DataHub Blog posts; comment out section if none -->

## FAQ and Troubleshooting

<!-- Use the following format:
**Question in bold text**
Response in plain text
-->

*Need more help? Join the conversation in [Slack](http://slack.datahubproject.io)!*

### Related Features

<!-- Bulleted list of related features; comment out section if none -->