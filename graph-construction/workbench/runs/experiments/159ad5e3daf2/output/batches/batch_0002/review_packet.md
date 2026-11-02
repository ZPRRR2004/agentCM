# 第 2 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：6–10
Prompt 版本：v0001
本批新增谓词：19
本批已有谓词修订：4
当前谓词总数：59

## 二、本批新增谓词

### PROBES_ENVIRONMENT_STATE

签名：`PROBES_ENVIRONMENT_STATE(action: action)`

The action performs a read-only inspection that queries the state, contents, installed software, or availability of the execution environment, in order to inform subsequent action selection.

参数：

- `action: action`：The read-only inspection or availability-check invocation.

成立条件：

- The action queries the state of the environment, resource, or service, such as which files or directories exist, which packages or versions are installed, or whether a network resource is reachable.
- The invocation is inspection-oriented: it does not install, write, delete, or perform the task's substantive computation.
- The information obtained is intended to determine what should be done next.

排除条件：

- The action modifies state, for example by installing, writing, or deleting.
- The action performs the task's main computation or produces the final deliverable.
- The action retrieves substantive task content for processing or transformation rather than checking what exists or is available.

### PROVISIONS_MISSING_CAPABILITY

签名：`PROVISIONS_MISSING_CAPABILITY(provisioning_action: action, absence_observation: observation)`

The action supplies a software capability — a library, package, tool, or runtime component — that an observation showed to be absent or insufficient, so that the intended operation can proceed.

参数：

- `provisioning_action: action`：The action installing, downloading, or otherwise providing the missing capability.
- `absence_observation: observation`：The observation stating or clearly implying that a required capability is missing or insufficient.

成立条件：

- The observation enumerates or reports environment contents in a way that states or clearly implies a required library, package, tool, or capability is missing or insufficient.
- The action installs, downloads, enables, or otherwise provisions that capability.
- The capability targeted by the action matches the one shown to be missing or insufficient.

排除条件：

- The observation only reports a successful state, available versions, or unrelated environment details.
- The action only checks availability without provisioning anything.
- The action provisions a capability unrelated to what the observation showed to be missing.
- The action re-executes a failed operation rather than supplying a missing capability.

### AUTHORS_EXECUTABLE_ARTIFACT

签名：`AUTHORS_EXECUTABLE_ARTIFACT(action: action)`

The action creates a file containing a program, script, or command sequence that is intended to be executed later to carry out the task.

参数：

- `action: action`：The file-writing action that authors the executable artifact.

成立条件：

- The action writes or creates a file.
- The file content is executable code or a command sequence rather than data, prose notes, or a final answer.
- The stated or evident purpose is that the artifact be run subsequently to accomplish the task.

排除条件：

- The action writes the final answer, a dataset, or another non-executable output.
- The action reads or edits an existing artifact without authoring executable content.
- The file is configuration, documentation, or a note not intended as an executable program.

### REVEALS_DATASET_SCHEMA

签名：`REVEALS_DATASET_SCHEMA(observation: observation)`

The observation exposes structured schema-level information about a data source, such as configuration or subset names, field or column names, data types, or split definitions.

参数：

- `observation: observation`：The observation containing structured schema, field, or configuration information for a data source.

成立条件：

- The observation enumerates or describes structured schema elements of a data source, such as configuration names, column or feature names, types, or splits.
- The information is specific enough to identify the individual fields or configurations available.

排除条件：

- The observation is free-form prose documentation without field-level or configuration-level structure.
- The observation only reports that a dataset exists, its size, or its file listing without schema details.
- The observation contains only raw records of data values without any schema description.

### ESTABLISHES_COMPUTATION_SPECIFICATION

签名：`ESTABLISHES_COMPUTATION_SPECIFICATION(reasoning: reasoning)`

The reasoning resolves an ambiguous or under-specified task by committing to a concrete interpretation and stating the data fields, filtering criterion, or computation procedure to apply.

参数：

- `reasoning: reasoning`：The reasoning text that interprets the task and fixes the computation to perform.

成立条件：

- The reasoning identifies an ambiguity or alternative plausible interpretations in the task requirements.
- The reasoning selects one concrete interpretation and states enough detail about the fields, filters, or operations to guide implementation.

排除条件：

- The reasoning only restates the task, or gives a general plan without concrete criteria.
- The reasoning reports results or execution rather than specifying the computation.
- The reasoning mentions fields or operations without resolving any ambiguity or under-specification.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(probe_action: action, assumption_reasoning: reasoning, probe_observation: observation)`

A targeted action empirically tests a specific assumption or ambiguity identified in prior reasoning, and the resulting observation provides evidence that resolves how that assumption affects the task.

参数：

- `probe_action: action`：The action performing the targeted empirical check.
- `assumption_reasoning: reasoning`：The reasoning explicitly identifying the assumption, ambiguity, or uncertainty to be tested.
- `probe_observation: observation`：The observation reporting the behavior relevant to the tested assumption.

成立条件：

- The assumption reasoning explicitly identifies an assumption or ambiguity whose truth could change the task result.
- The probe action is a focused check of that assumption, such as a small isolated test, diagnostic query, or controlled experiment, rather than the main computation.
- The probe observation reports behavior relevant to the assumption and supplies enough evidence to decide whether the assumption holds or how to interpret it.

排除条件：

- The action is the main computation or general exploration.
- No explicit assumption or uncertainty is identified in the reasoning.
- The probe result does not address the identified assumption.

### RESOLVES_TERM_AMBIGUITY_USING_REFERENCE

签名：`RESOLVES_TERM_AMBIGUITY_USING_REFERENCE(interpretation_reasoning: reasoning, reference_observation: observation, data_observation: observation)`

Reasoning resolves an underspecified or non-matching term from the task by combining a reference description with the category values actually observed in the data to select the concrete categories that the term denotes.

参数：

- `interpretation_reasoning: reasoning`：The reasoning that selects concrete categories as the meaning of the task term.
- `reference_observation: observation`：The observation supplying a taxonomy, grouping, or documentary description that relates observed categories to the term.
- `data_observation: observation`：The observation showing the category values actually present in the data.

成立条件：

- The data observation shows category labels or values that do not directly match the task term.
- The reference observation supplies a taxonomy, grouping, or documentary description relating the observed categories to the task term.
- The interpretation reasoning explicitly selects one or more observed categories as constituting the task term, using both the reference description and the observed values.

排除条件：

- The data already contains an exact matching category for the term.
- The mapping is asserted without documentary or other supporting evidence.
- The reasoning does not connect both the reference description and the observed values.
- The reasoning merely reports values without resolving the term.

### CROSS_VALIDATES_RESULT

签名：`CROSS_VALIDATES_RESULT(verification_action: action, original_result: observation, verification_result: observation)`

An independent verification action recomputes an already obtained result through a different data-access path or method, and the resulting observation reproduces the same value.

参数：

- `verification_action: action`：The action performing the independent recomputation.
- `original_result: observation`：The earlier observation reporting the originally computed value.
- `verification_result: observation`：The later observation reporting the independently recomputed value.

成立条件：

- The original result reports a computed value.
- The verification action uses an independent mechanism, such as a different library, data path, or algorithm, rather than repeating the same call.
- The verification result reports a value equal to the original result.

排除条件：

- The same procedure is repeated without an independent data-access path or method.
- The recomputed result differs from the original result.
- The verification only checks formatting or presence rather than reproducing the value.

### VERIFIES_ARTIFACT_BY_READBACK

签名：`VERIFIES_ARTIFACT_BY_READBACK(readback_action: action, artifact_content: observation)`

An action reads back a previously produced output artifact, and its resulting observation displays the stored content for confirmation.

参数：

- `readback_action: action`：The action that reads the stored output artifact.
- `artifact_content: observation`：The observation displaying the content of the stored artifact.

成立条件：

- A prior action produced or updated the output artifact.
- The readback action reads the stored artifact instead of recomputing or transforming the result.
- The artifact content observation displays content consistent with the intended output.

排除条件：

- The artifact was not previously produced or updated.
- The action recomputes or transforms the result rather than reading stored content.
- The observation does not display the artifact's content.

### IDENTIFIES_RETENTION_MECHANISM

签名：`IDENTIFIES_RETENTION_MECHANISM(reasoning: reasoning, retention_observation: observation)`

The reasoning explains why a target that should otherwise be absent remains present or reachable by attributing its continued availability to an identifiable retaining reference, log, cache, index, or equivalent persistence structure visible in an observation, and it selects a removal strategy aimed at that retaining mechanism.

参数：

- `reasoning: reasoning`：The agent text explaining continued retention and choosing a removal strategy.
- `retention_observation: observation`：The observation showing that the target remains present or reachable despite an apparent removal.

成立条件：

- retention_observation shows that the target remains present, reachable, or not reported as removed or dangling despite an apparent removal.
- The reasoning attributes continued availability to an identifiable reference, log, cache, index, or equivalent retention structure.
- The reasoning selects or proposes an operation that expires, disables, or purges that retaining mechanism.

排除条件：

- The reasoning only repeats a generic cleanup sequence without explaining retention.
- retention_observation already shows the target absent.
- The reasoning attributes retention vaguely without identifying an inspectable mechanism.

### ATTEMPTS_TO_ERASE_OBSERVED_ARTIFACT

签名：`ATTEMPTS_TO_ERASE_OBSERVED_ARTIFACT(erasure_action: action, exposure_observation: observation)`

The action performs deletion, expiration, pruning, or equivalent removal operations directed at target data — or at the object, reference, or structure retaining it — that a prior observation identified.

参数：

- `erasure_action: action`：The action attempting to delete, expire, or prune the target or its retaining structure.
- `exposure_observation: observation`：The prior observation identifying the target content, object, or retaining reference.

成立条件：

- exposure_observation identifies target content, an object containing it, or a reference retaining it.
- erasure_action deletes, expires, or prunes that object, reference, or containing structure.
- The action is directed at the observed target rather than being routine maintenance with no identified target.

排除条件：

- The action only inspects or verifies the target.
- The action removes files or history without evidence that they contain or retain the target.
- No prior observation identifies the target or its retaining structure.

### CONFIRMS_ERADICATION

签名：`CONFIRMS_ERADICATION(erasure_action: action, exposure_observation: observation, verification_observation: observation)`

An erasure action removes target data identified by an earlier observation, and a later verification observation establishes that the target is absent from the relevant searched scopes.

参数：

- `erasure_action: action`：The action removing the target or the structure retaining it.
- `exposure_observation: observation`：The earlier observation revealing the target content or retaining structure.
- `verification_observation: observation`：The later observation establishing that the target is absent.

成立条件：

- exposure_observation reveals target content or a structure retaining it.
- erasure_action deletes, expires, or prunes the target or retaining structure after that observation.
- verification_observation occurs after the erasure and reports the target not found across the relevant repository internals, revision history, and/or object storage, as applicable.
- The verification evidence shows no remaining searched object or reference containing the target.

排除条件：

- There is no erasure action or no subsequent verification observation.
- The verification finds the target or checks only an unrelated scope.
- The erasure action does not address the target identified by the exposure observation.

### VERIFIES_PRESERVATION_OF_UNRELATED_ARTIFACTS

签名：`VERIFIES_PRESERVATION_OF_UNRELATED_ARTIFACTS(reasoning: reasoning, verification_observation: observation)`

The reasoning uses a post-remediation observation to validate that artifacts unrelated to the target remain unchanged, by comparing their content, identifiers, or status with an earlier known state.

参数：

- `reasoning: reasoning`：The agent text validating that unrelated artifacts were preserved.
- `verification_observation: observation`：The post-remediation observation reporting content, identifiers, or status of non-target artifacts.

成立条件：

- verification_observation reports content, hashes, status, or identifiers of non-target artifacts after remediation.
- The reasoning explicitly compares that report with an earlier state or asserts identity and cleanliness of those artifacts.
- The preservation conclusion is tied to the reported evidence for those unrelated artifacts.

排除条件：

- Only target artifacts are examined.
- The reasoning assumes preservation without reported evidence from the observation.
- The observation predates the destructive or remediation action.

### PERFORMS_EXHAUSTIVE_UNIQUENESS_SEARCH

签名：`PERFORMS_EXHAUSTIVE_UNIQUENESS_SEARCH(search_action: action)`

The action enumerates the complete accessible object set, or an equivalent full corpus, and searches each item for the target pattern to determine whether the target occurs uniquely.

参数：

- `search_action: action`：The action enumerating objects or corpus items and searching them for the target.

成立条件：

- search_action enumerates all accessible objects, blobs, or corpus items rather than a sample.
- Each enumerated item is searched for the target pattern.
- The output associates occurrences with item identifiers or otherwise supports a uniqueness conclusion.

排除条件：

- The action searches only a single file, directory, or preselected subset.
- The action does not attempt to determine whether the target occurs more than once.
- Enumeration is incomplete so uniqueness cannot be established.

### PERFORMS_CROSS_SCOPE_ABSENCE_VERIFICATION

签名：`PERFORMS_CROSS_SCOPE_ABSENCE_VERIFICATION(verification_action: action)`

The action checks for a target across multiple independent storage scopes, such as working files, repository metadata, revision history, and object inventory, in order to confirm its absence rather than locate a present value.

参数：

- `verification_action: action`：The action checking multiple scopes for the target's absence.

成立条件：

- verification_action includes at least two independent searches or inspections for the target.
- The scopes cover different storage layers, histories, or metadata areas.
- The action is aimed at confirming absence rather than only locating a present target.

排除条件：

- The action performs a single grep or file check.
- The action checks only one storage layer.
- The action is not aimed at confirming absence.

### REPORTS_TARGET_ABSENT_ACROSS_SCOPES

签名：`REPORTS_TARGET_ABSENT_ACROSS_SCOPES(verification_observation: observation)`

The observation explicitly reports that the target was not found in multiple searched scopes and provides corroborating inventory or status evidence for absence.

参数：

- `verification_observation: observation`：The observation reporting not-found results and corroborating absence evidence.

成立条件：

- verification_observation contains explicit not-found results for at least two independent scopes.
- Corroborating evidence such as an object inventory, status, or remaining-content listing supports the absence claim.
- No execution error or ambiguity prevents interpreting the result as absence.

排除条件：

- Only one not-found result is reported.
- The command errored or output is ambiguous.
- The observation reports that the target is present.

### REPORTS_ENVIRONMENT_OR_ARTIFACT_STATE

签名：`REPORTS_ENVIRONMENT_OR_ARTIFACT_STATE(observation: observation)`

The observation enumerates concrete, factual state of the execution environment or of stored artifacts — such as directory contents, interpreter or library versions, installed packages, or retained/downloaded files with sizes — which can be used as operational ground truth.

参数：

- `observation: observation`：The tool result enumerating concrete environment or artifact facts.

成立条件：

- The observation content enumerates concrete facts such as file or directory names, version strings, installed packages, or retained assets, rather than only acknowledging an operation.
- The observation completes without an execution error that truncates or invalidates the enumeration.

排除条件：

- The observation returns an application response payload produced by a service endpoint.
- The observation reports an execution error or failure trace.
- The observation merely acknowledges that a write or other operation succeeded.
- The observation supplies schema-level definitions of a data source rather than environment or artifact state.

### CONFIRMS_EXTERNAL_REACHABILITY

签名：`CONFIRMS_EXTERNAL_REACHABILITY(action: action, observation: observation)`

A request contacts the running service through a host interface address other than the loopback address, and the resulting observation reports a successful response, establishing that the service is reachable beyond local-only access.

参数：

- `action: action`：The invocation that contacts the service through a non-loopback host interface address.
- `observation: observation`：The result of that request, indicating success or failure.

成立条件：

- The address targeted by the request is a host interface address other than localhost/127.0.0.1, such as a container or external interface address.
- The observation reports a successful response from the service at that address.

排除条件：

- The request targets localhost or 127.0.0.1.
- The request fails to reach the service, so external reachability is not confirmed.
- The evidence of availability is only a process listing, configuration value, or listening-socket entry rather than a successful remotely addressed request.

### ASSESSES_REQUIREMENTS_AS_SATISFIED

签名：`ASSESSES_REQUIREMENTS_AS_SATISFIED(reasoning: reasoning)`

The reasoning performs a final requirements assessment that maps multiple distinct requirements from the task specification to supporting evidence and concludes that all of them are satisfied.

参数：

- `reasoning: reasoning`：The agent text performing the final requirements assessment and declaring the requirements satisfied.

成立条件：

- The reasoning addresses multiple distinct requirements from the task specification.
- Each addressed requirement is marked as satisfied or verified, with reference to supporting evidence or observed behavior.
- The reasoning concludes that all requirements are fulfilled or declares the task complete.

排除条件：

- The reasoning reports only partial progress, unresolved issues, or remaining work.
- The reasoning lists or restates requirements without concluding that they are satisfied.
- The reasoning states a general completion claim without mapping individual requirements to supporting evidence.

## 三、本批已有谓词修订

### ATTEMPTS_REPAIR → ATTEMPTS_REPAIR

Window：xhigh__count-dataset-tokens__window_0001

修订前：

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action re-executes an operation whose prior result was inadequate — reporting an error or failing to produce the intended output — with the command, parameters, or environment changed so as to remove the identified cause.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure or the unusable result.

成立条件：

- The failure observation precedes the repair action and indicates that the operation did not succeed or did not produce the intended result.
- The action preserves the original goal while changing the element identified as faulty, such as an option's argument form, the scope of an environment setting, a path, an executing identity, or source content.

排除条件：

- The action repeats the inadequate invocation without any change.
- The action pursues a different goal unrelated to the reported result.
- No confirming evidence is required for this predicate; confirmation is a separate mechanism.

修订后：

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action makes a goal-preserving corrective re-attempt after an observation reported that an earlier attempt was unsuccessful or unusable, either changing the element identified as faulty or switching to a different route, tool, or method instead of repeating the attempt unchanged.

参数：

- `repair: action`：The action attempting the corrective re-attempt.
- `failure: observation`：The earlier observation reporting the failure or the unusable result.

成立条件：

- The failure observation precedes the repair action and indicates that the earlier attempt did not succeed or did not produce the intended result, whether through an error, a rejected response, or unusable output.
- The action preserves the original objective while changing the failing element — such as an argument form, path, scope setting, executing identity, or source content — or replacing the failed route, tool, or endpoint with an alternative.
- The change is motivated by the reported failure rather than being an unrelated new step.

排除条件：

- The action repeats the inadequate invocation unchanged.
- The action pursues a different objective unrelated to the reported result.
- No failure or unusable result is reported before the action; the action is an ordinary next step.
- Confirmation that the failure is resolved is not required for this predicate; it is a separate mechanism.

### VERIFIES_ARTIFACT_BY_READBACK → VERIFIES_ARTIFACT_BY_READBACK

Window：xhigh__git-leak-recovery__window_0001

修订前：

### VERIFIES_ARTIFACT_BY_READBACK

签名：`VERIFIES_ARTIFACT_BY_READBACK(readback_action: action, artifact_content: observation)`

An action reads back a previously produced output artifact, and its resulting observation displays the stored content for confirmation.

参数：

- `readback_action: action`：The action that reads the stored output artifact.
- `artifact_content: observation`：The observation displaying the content of the stored artifact.

成立条件：

- A prior action produced or updated the output artifact.
- The readback action reads the stored artifact instead of recomputing or transforming the result.
- The artifact content observation displays content consistent with the intended output.

排除条件：

- The artifact was not previously produced or updated.
- The action recomputes or transforms the result rather than reading stored content.
- The observation does not display the artifact's content.

修订后：

### VERIFIES_ARTIFACT_BY_READBACK

签名：`VERIFIES_ARTIFACT_BY_READBACK(readback_action: action, artifact_content: observation)`

An action reads back a previously produced or written output artifact from its destination, and the resulting observation provides content, size, or checksum evidence consistent with the intended value, confirming that the artifact was persisted with the intended content.

参数：

- `readback_action: action`：The action that reads the stored output artifact.
- `artifact_content: observation`：The observation displaying the stored artifact's content or reporting size or checksum evidence.

成立条件：

- A prior action produced, wrote, or updated the output artifact in its destination.
- The readback action reads the stored artifact rather than recomputing or transforming the result.
- The resulting observation displays stored content, or reports a size or checksum, consistent with the intended output value, serving as confirmation that the intended result was persisted.

排除条件：

- The artifact was not previously produced or written to the destination.
- The action recomputes or transforms the result rather than reading stored content.
- The observation does not display content and provides no size or checksum evidence of the artifact.
- The observed content or evidence differs from the intended target value.

### ESTABLISHES_COMPUTATION_SPECIFICATION → ESTABLISHES_COMPUTATION_SPECIFICATION

Window：xhigh__hf-model-inference__window_0001

修订前：

### ESTABLISHES_COMPUTATION_SPECIFICATION

签名：`ESTABLISHES_COMPUTATION_SPECIFICATION(reasoning: reasoning)`

The reasoning resolves an ambiguous or under-specified task by committing to a concrete interpretation and stating the data fields, filtering criterion, or computation procedure to apply.

参数：

- `reasoning: reasoning`：The reasoning text that interprets the task and fixes the computation to perform.

成立条件：

- The reasoning identifies an ambiguity or alternative plausible interpretations in the task requirements.
- The reasoning selects one concrete interpretation and states enough detail about the fields, filters, or operations to guide implementation.

排除条件：

- The reasoning only restates the task, or gives a general plan without concrete criteria.
- The reasoning reports results or execution rather than specifying the computation.
- The reasoning mentions fields or operations without resolving any ambiguity or under-specification.

修订后：

### ESTABLISHES_COMPUTATION_SPECIFICATION

签名：`ESTABLISHES_COMPUTATION_SPECIFICATION(reasoning: reasoning)`

The reasoning resolves an ambiguous or under-specified task requirement by committing to one concrete interpretation and stating the concrete specification — data fields, filtering criteria, computation procedure, or required behavior — that implementation should follow.

参数：

- `reasoning: reasoning`：The reasoning text that interprets the task and fixes the specification to implement.

成立条件：

- The reasoning identifies an ambiguity or alternative plausible interpretations in the task requirements.
- The reasoning selects one concrete interpretation and states enough detail about the fields, filters, operations, or required behavior to guide implementation.

排除条件：

- The reasoning only restates the task, or gives a general plan without concrete criteria.
- The reasoning reports results or execution rather than specifying the computation.
- The reasoning mentions fields or operations without resolving any ambiguity or under-specification.
- The ambiguity concerns tool availability or environment state rather than requirement semantics.

### GROUNDS_CONCLUSION_IN_OBSERVATION → GROUNDS_CONCLUSION_IN_OBSERVATION

Window：xhigh__hf-model-inference__window_0002

修订前：

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning reaches a conclusion or makes a decision that relies on identifiable values, entries, or findings supplied by a prior observation.

参数：

- `reasoning: reasoning`：The reasoning that reaches the conclusion or decision.
- `observation: observation`：The prior observation supplying the substantive content used by the reasoning.

成立条件：

- A conclusion, decision, or derived value in the reasoning can be traced to specific substantive content of the observation.
- The observation precedes the reasoning and contributes data rather than only a success or failure indication.

排除条件：

- The observation only reports tool success or failure without substantive content used by the reasoning.
- The reasoning is only topically related to the observation and does not use its values.
- The conclusion is reached independently of the observation.

修订后：

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning reaches a conclusion or makes a decision that relies on identifiable content supplied by a prior observation — such as values, entries, statuses, response bodies, or environment and process listings — using that content as evidence for the stated conclusion.

参数：

- `reasoning: reasoning`：The reasoning that reaches the conclusion or decision.
- `observation: observation`：The prior observation supplying the content used as evidence by the reasoning.

成立条件：

- A conclusion, decision, or derived value in the reasoning can be traced to specific content of the observation.
- The observation precedes the reasoning and supplies evidence that the reasoning uses to support its stated conclusion.

排除条件：

- The reasoning only describes a plan, or repeats the observation without drawing a conclusion.
- The observation is merely topically related and supplies no traceable evidential value for the conclusion.
- The conclusion is reached independently of the observation.

## 四、当前完整 Registry

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent intends to carry out next.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action or sequence of actions.

成立条件：

- The reasoning identifies at least one action to be performed later, such as inspecting a file, writing content, compiling, or verifying output.
- The intended action is stated prospectively rather than reported as already done.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning only restates file content or tool output without expressing an intended next action.

### DIAGNOSES_OBSERVED_FAILURE

签名：`DIAGNOSES_OBSERVED_FAILURE(reasoning: reasoning, failure: observation)`

The reasoning explains the cause of a failure reported by an observation and derives a corrective approach from that explanation.

参数：

- `reasoning: reasoning`：The agent text explaining why the observed failure occurred and what should change.
- `failure: observation`：The observation reporting the failure being explained.

成立条件：

- The observation indicates that an invoked operation did not succeed.
- The reasoning identifies a concrete cause for the failure and states a corrective approach or change based on that cause.

排除条件：

- The reasoning merely notes that something failed without offering a causal explanation.
- The reasoning explains an unrelated issue or offers no corrective direction.

### GUIDES_ACTION

签名：`GUIDES_ACTION(reasoning: reasoning, action: action)`

The action's tool choice, target, or argument values instantiate an intent, diagnosis, or corrected approach explicitly stated in the reasoning.

参数：

- `reasoning: reasoning`：The agent text stating the plan, diagnosis, or corrected approach.
- `action: action`：The action whose tool, target, or arguments carry out that stated approach.

成立条件：

- The reasoning specifies the operation or correction to perform, and the action performs that same operation with matching target or arguments.
- A traceable correspondence exists between the described step and the executed parameters, command, path, or content.

排除条件：

- The action is unrelated to the described step or diverges from it in target or approach.
- The reasoning only reports prior results and the action is merely temporally adjacent.

### USES_OBSERVATION_AS_INPUT

签名：`USES_OBSERVATION_AS_INPUT(action: action, observation: observation)`

The action uses an identifiable value or payload supplied by a prior observation as an operational input.

参数：

- `action: action`：The action receiving the input.
- `observation: observation`：The prior observation supplying the input value or payload.

成立条件：

- An argument, file content, path, or identifier of the action can be traced to content present in the observation.
- The observation precedes the action within the trajectory.

排除条件：

- The observation only guides action selection without supplying an operational input value.
- The nodes are merely temporally adjacent or topically related without a traceable value transfer.

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(repair: action, failure: observation)`

The action makes a goal-preserving corrective re-attempt after an observation reported that an earlier attempt was unsuccessful or unusable, either changing the element identified as faulty or switching to a different route, tool, or method instead of repeating the attempt unchanged.

参数：

- `repair: action`：The action attempting the corrective re-attempt.
- `failure: observation`：The earlier observation reporting the failure or the unusable result.

成立条件：

- The failure observation precedes the repair action and indicates that the earlier attempt did not succeed or did not produce the intended result, whether through an error, a rejected response, or unusable output.
- The action preserves the original objective while changing the failing element — such as an argument form, path, scope setting, executing identity, or source content — or replacing the failed route, tool, or endpoint with an alternative.
- The change is motivated by the reported failure rather than being an unrelated new step.

排除条件：

- The action repeats the inadequate invocation unchanged.
- The action pursues a different objective unrelated to the reported result.
- No failure or unusable result is reported before the action; the action is an ordinary next step.
- Confirmation that the failure is resolved is not required for this predicate; it is a separate mechanism.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, check_result: observation)`

A repair action addresses an observed failure, and a subsequent execution result confirms that the original failure has been resolved.

参数：

- `repair: action`：The action attempting to repair the failure.
- `failure: observation`：The earlier observation reporting the failure.
- `check_result: observation`：The later observation establishing that the original failure no longer occurs.

成立条件：

- The failure precedes the repair, and the repair changes the failing element.
- The later result shows the target operation or content being produced, loaded, or otherwise completed successfully, with no recurrence of the original error.

排除条件：

- The repair is attempted without any later result.
- The later output repeats the original error or otherwise fails to establish resolution.

### REPORTS_FAILURE

签名：`REPORTS_FAILURE(observation: observation)`

The observation indicates that the invoked operation did not succeed.

参数：

- `observation: observation`：The tool result being evaluated for failure.

成立条件：

- The observation carries an error indication, a non-success exit status, or an explicit error message such as a missing file or unloadable module.

排除条件：

- The observation reports successful completion or plain data output without any error indication.

### REPORTS_SUCCESS

签名：`REPORTS_SUCCESS(observation: observation)`

The observation indicates that the invoked operation completed successfully.

参数：

- `observation: observation`：The tool result being evaluated for success.

成立条件：

- The observation contains an explicit success message, a clean completion with no error indication, or a listing of the expected produced artifacts.

排除条件：

- The observation reports an error or non-success exit status.
- The output is only a partial or ambiguous progress message.

### IS_COMPLETION_CONCLUSION

签名：`IS_COMPLETION_CONCLUSION(reasoning: reasoning)`

The reasoning declares the overall objective achieved and cites the verification evidence that supports the claim.

参数：

- `reasoning: reasoning`：The agent text asserting task completion.

成立条件：

- The reasoning states that the requested objective has been fulfilled.
- It references concrete evidence obtained earlier, such as produced artifacts or verified output.

排除条件：

- The reasoning states plans or intermediate steps while work remains.
- The reasoning reports observations without concluding that the objective is achieved.

### IDENTIFIES_MISSING_SOFTWARE_DEPENDENCY

签名：`IDENTIFIES_MISSING_SOFTWARE_DEPENDENCY(reasoning: reasoning, observation: observation)`

The reasoning interprets an environment probe as showing that software required for the task is absent and treats obtaining that software as a prerequisite for proceeding with the intended configuration.

参数：

- `reasoning: reasoning`：The agent text diagnosing the environment and naming the missing capability.
- `observation: observation`：The probe result showing which required tools or services are absent.

成立条件：

- The observation reports probe results about the environment, such as available binaries, packages, or running processes, and shows that one or more task-required tools or services are unavailable.
- The reasoning explicitly connects that absence to the task and indicates that the missing software must be supplied before the intended work can proceed.

排除条件：

- The observation merely enumerates installed software or environment details without revealing a missing task requirement.
- The reasoning restates the task or lists actions without connecting an observed absence to a prerequisite that must be supplied.
- The reasoning explains a failed operation rather than an absent prerequisite.

### ADAPTS_TO_ABSENT_SERVICE_MANAGER

签名：`ADAPTS_TO_ABSENT_SERVICE_MANAGER(reasoning: reasoning, observation: observation)`

The reasoning infers from a process or runtime observation that no conventional service manager or init system is available, and consequently adopts direct or manual control of services instead of the usual management mechanism.

参数：

- `reasoning: reasoning`：The agent text inferring the absence of an init or service manager and adapting the startup strategy.
- `observation: observation`：The process or runtime listing showing that the environment lacks a conventional service manager.

成立条件：

- The observation exposes process or runtime state showing that the environment is not controlled by a conventional init or service manager.
- The reasoning explicitly concludes that services cannot be managed through that absent mechanism and selects direct daemon startup, manual supervision, or an equivalent non-init strategy.

排除条件：

- The observation does not expose process or runtime state relevant to how services are managed.
- The reasoning plans service startup without noting that a management mechanism is absent.
- A service manager is present and the reasoning uses it in the usual way.

### PREPARES_ACCOUNT_FOR_KEY_AUTHENTICATION

签名：`PREPARES_ACCOUNT_FOR_KEY_AUTHENTICATION(action: action)`

The action configures a service account with a usable login environment and a non-locking authentication state, together with key-access ownership and permissions, so the account can be reached remotely without password login and can own the service's data.

参数：

- `action: action`：The account-creation and authentication-state adjustment command or script.

成立条件：

- The action creates or selects an account with a usable login shell and home directory.
- The action places the account's authentication state in a non-locking form so that key-based login is not rejected.
- The action creates a user-owned .ssh directory with restrictive permissions and an authorized-keys file ready to receive public keys.

排除条件：

- The action creates an account but leaves it locked or otherwise unable to accept key-based login.
- The action adjusts unrelated account attributes without preparing remote key-based access.

### INITIALIZES_BARE_REPOSITORY

签名：`INITIALIZES_BARE_REPOSITORY(action: action)`

The action establishes a bare repository as a push target at the intended service location, points its default branch reference at the branch clients will push, and places it under ownership that allows the service account to receive pushes.

参数：

- `action: action`：The repository initialization, branch-reference, and ownership command.

成立条件：

- The action creates a bare repository at the intended service path.
- The action sets HEAD or an equivalent symbolic reference to the designated default branch.
- The action assigns repository ownership or equivalent write authority to the service account.

排除条件：

- The action initializes a non-bare working repository rather than a push target.
- The repository is left without the intended default branch or without ownership permitting the service account to receive pushes.

### CONFIGURES_PUSH_TRIGGERED_DEPLOYMENT

签名：`CONFIGURES_PUSH_TRIGGERED_DEPLOYMENT(action: action)`

The action installs an executable repository hook that reacts to pushed branch references by deploying the pushed content into the directory served by the web server.

参数：

- `action: action`：The hook-writing or hook-installation action.

成立条件：

- The action writes an executable hook into the repository's hook directory.
- The hook logic reads pushed references and performs a work-tree checkout or equivalent deployment into the served document root.
- The hook limits deployment to branch updates and excludes non-branch or branch-deletion events.

排除条件：

- The hook only logs, notifies, or performs an action unrelated to deploying pushed content.
- Deployment into the served directory is not part of the hook behavior.

### CONFIGURES_SERVICE_ENDPOINT

签名：`CONFIGURES_SERVICE_ENDPOINT(action: action)`

The action writes or replaces the active configuration of a network service so that the service listens on the task-required port and serves content from the intended document root.

参数：

- `action: action`：The configuration-writing action that defines the service endpoint.

成立条件：

- The configuration specifies the task-required listen port.
- The configuration specifies the document root from which content should be served.
- The configuration is written to an active configuration location or to one that the service loads.

排除条件：

- The action edits an inactive or sample configuration that the service does not load.
- The action changes unrelated directives without defining the required port and document root.

### PREPARES_DEPLOYMENT_DIRECTORY

签名：`PREPARES_DEPLOYMENT_DIRECTORY(action: action)`

The action prepares the directory served by the web server so that the deployment account can write pushed content into it while the server process retains read access to that content.

参数：

- `action: action`：The directory-creation and ownership or permission adjustment command.

成立条件：

- The action creates the served directory or confirms that it exists.
- The action assigns ownership or permissions that allow the deployment account to write into the directory.
- The resulting ownership and permissions leave the content readable by the web server process.

排除条件：

- The action only reads or lists the directory without preparing it for deployment.
- The action changes ownership or permissions in a way that prevents the web server process from reading deployed content.

### VALIDATES_AND_ENABLES_SERVICE_CONFIGURATION

签名：`VALIDATES_AND_ENABLES_SERVICE_CONFIGURATION(action: action)`

The action confirms that the intended service configuration is enabled and syntactically valid, and makes service startup conditional on that confirmation succeeding.

参数：

- `action: action`：The validation and activation command sequence.

成立条件：

- The action checks whether the intended configuration is enabled or linked into the active configuration set.
- The action runs a syntax or consistency check on the service configuration.
- Startup of the service is chained to the success of the check.

排除条件：

- The service is started without any configuration validation.
- A validation command is run but its failure does not prevent startup.

### STARTS_SERVICE_DAEMONS_DIRECTLY

签名：`STARTS_SERVICE_DAEMONS_DIRECTLY(action: action)`

The action launches the required long-running service daemons directly rather than through a service manager, preparing any runtime prerequisites those daemons need in order to start and remain running.

参数：

- `action: action`：The daemon-launching command or script.

成立条件：

- The action invokes daemon binaries or equivalent direct start commands for the required network services.
- The action prepares runtime prerequisites such as directories, host keys, or runtime state needed for those daemons to start.
- The launched processes are intended to remain running after the invoking command returns.

排除条件：

- The action only installs packages without launching the services.
- The action delegates startup to a service manager or init system.
- The action starts only a transient foreground process instead of the required long-running daemon.

### ESTABLISHES_LOCAL_HOSTNAME_RESOLUTION

签名：`ESTABLISHES_LOCAL_HOSTNAME_RESOLUTION(action: action)`

The action adds a local name-resolution mapping so that the hostname used in the task's client commands resolves to the local or container-reachable address of the service.

参数：

- `action: action`：The hostname or resolver configuration action.

成立条件：

- The action adds or modifies a local hosts-file or equivalent resolver entry.
- The entry maps the task's service hostname to an address that reaches the local service.

排除条件：

- The action changes the machine's own hostname rather than adding a service-name mapping.
- The action only relies on external name resolution without adding the local mapping.

### GUIDES_CONFIGURATION_CHANGE

签名：`GUIDES_CONFIGURATION_CHANGE(observation: observation, action: action)`

An observation exposes the current structure or values of a service configuration, and a subsequent action rewrites that same configuration to the task-required values, using the observed structure to locate or shape the change.

参数：

- `observation: observation`：The observation revealing existing configuration values or activation structure.
- `action: action`：The later action that rewrites the observed configuration.

成立条件：

- The observation shows current configuration details such as a listen directive, a document root, or the active-configuration linkage.
- A subsequent action writes or replaces that same configuration, changing the identified values to the task-required values.
- The correspondence between the observed configuration and the rewritten configuration is identifiable as the same file or the same service configuration.

排除条件：

- The observation supplies an operational data value rather than configuration structure or values.
- The subsequent action modifies an unrelated configuration without using the observed structure or values.
- The action writes a configuration without any prior inspection of that configuration.

### PLANS_END_TO_END_VERIFICATION

签名：`PLANS_END_TO_END_VERIFICATION(reasoning: reasoning)`

The reasoning lays out a forthcoming verification procedure that reproduces the requester's prescribed end-user workflow against the configured system, and identifies the observable outcome by which the procedure's success will be judged.

参数：

- `reasoning: reasoning`：The agent text that specifies the forthcoming validation procedure and its expected outcome.

成立条件：

- The reasoning names at least one end-user interaction from the request, such as authenticating, cloning, committing, pushing, or retrieving the deployed path, as something to be executed for validation.
- The reasoning identifies the observable result that the procedure should produce, so that success can be judged.

排除条件：

- The reasoning only describes configuration changes or service management to be performed.
- The reasoning only reports results of checks already completed, without specifying a forthcoming verification procedure.
- The reasoning plans only an internal or intermediate check that does not exercise the requester's end-user interaction.

### EXECUTES_USER_WORKFLOW_TRIAL

签名：`EXECUTES_USER_WORKFLOW_TRIAL(action: action)`

The action runs the requester's prescribed end-user command sequence, or a faithful stand-in for it, against the configured system as a functional acceptance trial of the delivered capability rather than as configuration or state inspection.

参数：

- `action: action`：The tool invocation that exercises the user-facing flow end to end.

成立条件：

- The invocation contains commands reproducing the end-user interaction from the request, such as a remote clone followed by commit and push, or a retrieval of the deployed path.
- The invocation occurs after the relevant configuration has been applied, so that its result reflects the delivered capability.

排除条件：

- The invocation only edits configuration files, starts services, or inspects filesystem or process state.
- The invocation exercises only an internal component rather than the requester-visible flow.
- The invocation merely prepares or cleans up the trial environment without exercising the user-facing flow.

### OBSERVATION_CONFIRMS_REQUESTED_BEHAVIOR

签名：`OBSERVATION_CONFIRMS_REQUESTED_BEHAVIOR(observation: observation)`

The observation carries the outcome of a user-facing interaction whose content matches the end-user-visible behavior specified in the request, providing direct evidence that the delivered system produces the requested result.

参数：

- `observation: observation`：The tool result carrying the outcome of the user-facing interaction.

成立条件：

- The output contains the result the requester stated they expect, such as served content equal to the specified payload or the expected response from the retrieved resource.
- The result is returned without an error status or failure indication.

排除条件：

- The output shows only configuration, process, or filesystem state.
- The output differs from the requested result, is empty, or reports an error or missing resource.

### OBSERVATION_CONFIRMS_SERVICE_AVAILABILITY

签名：`OBSERVATION_CONFIRMS_SERVICE_AVAILABILITY(observation: observation)`

The observation provides evidence that the required long-running services are active and reachable, through live process entries or through listening-socket entries for the required ports.

参数：

- `observation: observation`：The tool result listing running processes or listening sockets.

成立条件：

- The output shows running process instances for the required daemons, or sockets in the listening state for the required ports.
- The evidence is produced without error markers or missing entries for the required services.

排除条件：

- The output is only a configuration syntax validation or a confirmation that a file was written or edited.
- The output names the services but gives no indication that processes are running or ports are listening.

### ATTRIBUTES_FAILURE_TO_TRIAL_SETUP

签名：`ATTRIBUTES_FAILURE_TO_TRIAL_SETUP(reasoning: reasoning, observation: observation)`

The reasoning concludes that an observed failure originates in the agent's own trial setup or command construction rather than in the delivered system, so no change to the delivered configuration is required.

参数：

- `reasoning: reasoning`：The agent text classifying the origin of the failure.
- `observation: observation`：The tool result reporting the failure whose origin is being classified.

成立条件：

- The reasoning explicitly links the failure to a characteristic of the trial environment or of how the trial command was assembled.
- The reasoning states that the delivered system itself remains correct, or that the failure would not occur for the requester.

排除条件：

- The reasoning treats the failure as a defect of the delivered system.
- The reasoning does not distinguish trial-induced failure from genuine system failure.

### JUDGES_OBSERVATION_CONCLUSIVENESS

签名：`JUDGES_OBSERVATION_CONCLUSIVENESS(reasoning: reasoning, observation: observation)`

The reasoning assesses whether an indirect, low-detail, or empty observation is sufficient to establish the intended property, drawing on auxiliary cues such as reported size, known content, structural knowledge, or tool behavior.

参数：

- `reasoning: reasoning`：The agent text assessing the evidential value of the observation.
- `observation: observation`：The low-detail, empty, or indirect tool result being assessed.

成立条件：

- The reasoning explains why the observation's content, or its absence of output, does or does not establish the target property.
- When the evidence is judged insufficient, the reasoning states what alternative evidence or check is required.

排除条件：

- The reasoning accepts the observation's output at face value without evaluating its sufficiency.
- The reasoning addresses a different observation than the one being judged.

### DELEGATES_OPERATION_TO_RESOURCE_OWNER

签名：`DELEGATES_OPERATION_TO_RESOURCE_OWNER(action: action, rejection: observation)`

In response to a reported ownership or permission refusal, the action performs the rejected operation under the identity that owns the resource instead of the rejected identity.

参数：

- `action: action`：The invocation that re-executes the operation under the owning identity.
- `rejection: observation`：The earlier tool result reporting the ownership or permission error.

成立条件：

- The earlier observation contains an ownership or permission refusal that names the resource.
- The action switches the executing identity to the owning account while preserving the operation's target and intent.

排除条件：

- The earlier error concerns connectivity, availability, or a missing file rather than ownership or permission.
- The action resolves the refusal by changing the resource's ownership or permissions instead of changing the executing identity.
- The action continues to run under the rejected identity.

### CLEANS_TEST_ARTIFACTS

签名：`CLEANS_TEST_ARTIFACTS(action: action)`

The action removes or reverts state created during the agent's own trials — temporary credentials, cloned working copies, scratch directories, trial commits and pushed references, and files deployed by the trials — so the delivered system returns to the pristine state expected immediately before the requester's own first operation, while leaving the configured services and permanent infrastructure intact.

参数：

- `action: action`：The cleanup invocation removing trial-created state.

成立条件：

- The invocation deletes or resets entities that the trials created, such as temporary keys, test clones, scratch directories, test commits or branch references, and files deployed by the trials.
- The invocation restores the initial structural state of the affected locations, such as an empty reference set in the repository, an empty document root, or a credentials file ready to receive the requester's own key.
- The invocation leaves the configured services, account setup, and permanent configuration in place, so the requester's commands still succeed afterwards.

排除条件：

- The invocation only performs routine configuration or service management.
- The invocation deletes resources that belong to the delivered system rather than to the trials.
- The invocation only inspects state without modifying it.
- The reset is performed to repair a reported failure rather than to return the system to its pristine pre-trial state.

### PRESERVES_USER_COMMAND_PRECONDITIONS

签名：`PRESERVES_USER_COMMAND_PRECONDITIONS(reasoning: reasoning)`

The reasoning identifies residual state that would cause the requester's own prescribed commands to fail or misbehave, and concludes that this state must be removed or reverted before handoff.

参数：

- `reasoning: reasoning`：The agent text linking leftover state to a concrete failure in the requester's command sequence.

成立条件：

- The reasoning identifies a specific leftover artifact, such as an already-existing commit or an already-deployed file.
- The reasoning names the concrete command from the request that would fail or misbehave because of that artifact, and calls for reverting it.

排除条件：

- The reasoning argues only for general tidiness without naming a command that would fail.
- The reasoning concludes that the leftover state is harmless for the requester's commands.

### JUSTIFIES_PREPARED_HANDOFF_STATE

签名：`JUSTIFIES_PREPARED_HANDOFF_STATE(reasoning: reasoning)`

The reasoning justifies deliberately leaving a pre-created but empty or inert artifact in place, rather than deleting or pre-populating it, because keeping it lets the requester's own subsequent manual step succeed without extra work.

参数：

- `reasoning: reasoning`：The agent text weighing removal against retention of a prepared artifact.

成立条件：

- The reasoning compares removing the prepared artifact with keeping it in an empty or inert form.
- The reasoning concludes that keeping it lets the requester's own setup step succeed without extra work.

排除条件：

- The reasoning only plans removal of the artifact.
- The reasoning pre-populates functional data that the requester is supposed to supply themselves.

### DERIVES_STATE_FROM_RAW_OUTPUT

签名：`DERIVES_STATE_FROM_RAW_OUTPUT(reasoning: reasoning, observation: observation)`

The reasoning translates low-level, encoded, or procedural output in the observation into an explicit semantic conclusion about the state of the system.

参数：

- `reasoning: reasoning`：The agent text that decodes the raw output into a stated system state.
- `observation: observation`：The tool result containing encoded, numeric, or procedural output such as hexadecimal socket entries and state codes, ref listings, or transfer logs.

成立条件：

- The observation contains tokens that are not directly human-meaningful, such as hexadecimal socket addresses and state codes, encoded status fields, ref listings, or version-control transfer transcripts.
- The reasoning explicitly maps those tokens to named system states, for example which ports are listening, which interfaces the services are bound to, or that a pushed branch was published.
- The stated conclusion is presented as the meaning of the observed output rather than as an independent guess.

排除条件：

- The observation already states a plain semantic conclusion that the reasoning only repeats.
- The reasoning quotes the output without assigning it a system-state meaning.
- The reasoning speculates about system state without grounding the conclusion in the observed tokens.
- The reasoning evaluates whether the observation is sufficient evidence rather than decoding its content.

### INSTALLS_STARTUP_HOOK_FOR_ARTIFACT

签名：`INSTALLS_STARTUP_HOOK_FOR_ARTIFACT(registration_action: action, creation_action: action)`

The later action registers an artifact created by an earlier action in shell, session, or system startup configuration so that the artifact is invoked automatically in future contexts, without altering the artifact's own content.

参数：

- `registration_action: action`：The action that writes or appends startup or session-initialization configuration referencing the artifact.
- `creation_action: action`：The earlier action that created the artifact being registered.

成立条件：

- The creation action produced a named executable, script, or configuration artifact whose creation is evidenced by its result.
- The registration action adds references to that artifact path in one or more startup or session-initialization files, such as a shell rc file, a profile drop-in, or an equivalent.
- The registration action leaves the artifact's content unchanged and only controls when or whether it is invoked.

排除条件：

- The artifact registered was not created by the earlier action in the same trajectory.
- The later action modifies or rewrites the artifact itself instead of registering it.
- The registration only applies an ownership or permission change without arranging automatic invocation.
- The two actions are only temporally adjacent and operationally unrelated.

### EXPLAINS_ANOMALY_AS_HARMLESS

签名：`EXPLAINS_ANOMALY_AS_HARMLESS(reasoning: reasoning, observation: observation)`

The reasoning investigates an anomalous condition visible in the observation, identifies its cause, and concludes that the anomaly does not affect the required functionality, relying on functional evidence rather than altering the configuration.

参数：

- `reasoning: reasoning`：The agent text that diagnoses and judges the anomalous condition.
- `observation: observation`：The tool result exhibiting the anomalous condition.

成立条件：

- The observation shows a condition that deviates from a clean expected state, such as lingering defunct processes, unexpected extra or missing entries, or an unexpectedly empty result.
- The reasoning offers a causal explanation for the anomaly that places its origin outside the delivered functionality.
- The reasoning concludes that the anomaly is cosmetic or non-impacting, citing evidence that the required functionality still succeeds, such as a fresh successful operation or a previously verified user-visible result.

排除条件：

- The anomaly is observed but not explained.
- The anomaly prompts a repair or configuration change.
- The reasoning asserts the condition is harmless without any causal account or functional evidence.
- The reasoning treats the anomaly as a defect of the delivered system.

### RESOLVES_DATA_INCONSISTENCY

签名：`RESOLVES_DATA_INCONSISTENCY(reasoning: reasoning)`

The reasoning detects a discrepancy or conflict among observed data — such as an unexpected mismatch between a container's label and the identifiers or attributes embedded in it — and resolves it by deciding how that data should be interpreted for the task.

参数：

- `reasoning: reasoning`：The agent text detecting the discrepancy and deciding how to interpret the data.

成立条件：

- The reasoning identifies a concrete conflict or unexpected mismatch in the observed data, for example between file names and the identifiers, labels, or attributes found inside them.
- The reasoning weighs the competing interpretations and adopts a decision about which interpretation to use, or concludes that the discrepancy does not affect the task.

排除条件：

- The reasoning merely quotes, summarizes, or reformats the observed data without noticing a discrepancy.
- A discrepancy is noted but its interpretation is left unresolved.
- The observed differences are ordinary expected variation rather than a conflict that requires interpretation.

### DERIVES_CONSTRAINED_SOLUTION

签名：`DERIVES_CONSTRAINED_SOLUTION(reasoning: reasoning)`

The reasoning derives a concrete solution by applying explicit constraints to candidate values, eliminating or comparing alternatives, and selecting a specific result.

参数：

- `reasoning: reasoning`：The agent text deriving the constrained solution.

成立条件：

- The reasoning applies stated constraints, limits, or preferences to candidate values.
- The reasoning compares alternatives or rules them out as infeasible.
- The reasoning states a specific selected solution, including any tie-breaker applied when several candidates remain.

排除条件：

- The reasoning only restates requirements or enumerates raw data.
- A candidate is proposed without being checked against the stated constraints.
- No concrete result is selected.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning reaches a conclusion or makes a decision that relies on identifiable content supplied by a prior observation — such as values, entries, statuses, response bodies, or environment and process listings — using that content as evidence for the stated conclusion.

参数：

- `reasoning: reasoning`：The reasoning that reaches the conclusion or decision.
- `observation: observation`：The prior observation supplying the content used as evidence by the reasoning.

成立条件：

- A conclusion, decision, or derived value in the reasoning can be traced to specific content of the observation.
- The observation precedes the reasoning and supplies evidence that the reasoning uses to support its stated conclusion.

排除条件：

- The reasoning only describes a plan, or repeats the observation without drawing a conclusion.
- The observation is merely topically related and supplies no traceable evidential value for the conclusion.
- The conclusion is reached independently of the observation.

### GENERATES_DELIVERABLE_ARTIFACT

签名：`GENERATES_DELIVERABLE_ARTIFACT(action: action)`

The action writes a complete artifact to the task-designated output location, serving as the substantive deliverable of the task.

参数：

- `action: action`：The write action producing the deliverable artifact.

成立条件：

- The action is a write-type operation targeting the output location that the task designates for the deliverable.
- The written content is a complete artifact in the required format carrying the requested payload.

排除条件：

- The action writes an auxiliary script, temporary file, or partial snippet.
- The action reads rather than writes data.
- The action writes outside the designated deliverable location.

### AUTHORS_VALIDATION_PROGRAM

签名：`AUTHORS_VALIDATION_PROGRAM(action: action)`

The action creates or rewrites an executable program whose purpose is to check an artifact or solution against stated requirements and report pass/fail results.

参数：

- `action: action`：The write action authoring the validation program.

成立条件：

- The action writes executable code implementing validation logic.
- The program checks format, constraints, or correctness of an artifact or solution and emits an explicit pass/fail or error outcome.

排除条件：

- The action writes the data deliverable itself rather than a validator.
- The action runs an existing validator without authoring or rewriting its code.
- The action writes prose, data, or an incomplete snippet rather than an executable validation program.

### EXECUTES_VALIDATION_PROGRAM

签名：`EXECUTES_VALIDATION_PROGRAM(action: action)`

The action executes a program or script in order to check an artifact or solution against requirements and obtain verification evidence.

参数：

- `action: action`：The action executing the validation program.

成立条件：

- The tool invocation runs validation logic against an artifact or solution.
- The invocation's purpose is to assess correctness, and its result supplies pass/fail verification evidence.

排除条件：

- The action only reads, writes, or inspects the artifact without running validation logic.
- The action runs a command unrelated to assessing correctness.
- The action only authors validation code without executing it.

### CHECKS_INPUT_INTEGRITY

签名：`CHECKS_INPUT_INTEGRITY(action: action)`

The action performs read-only inspection of task input files' listing, metadata, or checksums in order to confirm that those inputs remain unmodified.

参数：

- `action: action`：The action inspecting the input files for integrity.

成立条件：

- The action inspects existing input files without altering them, for example by listing them with metadata or computing checksums.
- The inspection is aimed at confirming that the task inputs have not been modified.

排除条件：

- The action reads input content for task analysis rather than for verifying that inputs are unchanged.
- The action modifies or deletes input files.
- The action only checks the produced output artifact.

### PROBES_ENVIRONMENT_STATE

签名：`PROBES_ENVIRONMENT_STATE(action: action)`

The action performs a read-only inspection that queries the state, contents, installed software, or availability of the execution environment, in order to inform subsequent action selection.

参数：

- `action: action`：The read-only inspection or availability-check invocation.

成立条件：

- The action queries the state of the environment, resource, or service, such as which files or directories exist, which packages or versions are installed, or whether a network resource is reachable.
- The invocation is inspection-oriented: it does not install, write, delete, or perform the task's substantive computation.
- The information obtained is intended to determine what should be done next.

排除条件：

- The action modifies state, for example by installing, writing, or deleting.
- The action performs the task's main computation or produces the final deliverable.
- The action retrieves substantive task content for processing or transformation rather than checking what exists or is available.

### PROVISIONS_MISSING_CAPABILITY

签名：`PROVISIONS_MISSING_CAPABILITY(provisioning_action: action, absence_observation: observation)`

The action supplies a software capability — a library, package, tool, or runtime component — that an observation showed to be absent or insufficient, so that the intended operation can proceed.

参数：

- `provisioning_action: action`：The action installing, downloading, or otherwise providing the missing capability.
- `absence_observation: observation`：The observation stating or clearly implying that a required capability is missing or insufficient.

成立条件：

- The observation enumerates or reports environment contents in a way that states or clearly implies a required library, package, tool, or capability is missing or insufficient.
- The action installs, downloads, enables, or otherwise provisions that capability.
- The capability targeted by the action matches the one shown to be missing or insufficient.

排除条件：

- The observation only reports a successful state, available versions, or unrelated environment details.
- The action only checks availability without provisioning anything.
- The action provisions a capability unrelated to what the observation showed to be missing.
- The action re-executes a failed operation rather than supplying a missing capability.

### AUTHORS_EXECUTABLE_ARTIFACT

签名：`AUTHORS_EXECUTABLE_ARTIFACT(action: action)`

The action creates a file containing a program, script, or command sequence that is intended to be executed later to carry out the task.

参数：

- `action: action`：The file-writing action that authors the executable artifact.

成立条件：

- The action writes or creates a file.
- The file content is executable code or a command sequence rather than data, prose notes, or a final answer.
- The stated or evident purpose is that the artifact be run subsequently to accomplish the task.

排除条件：

- The action writes the final answer, a dataset, or another non-executable output.
- The action reads or edits an existing artifact without authoring executable content.
- The file is configuration, documentation, or a note not intended as an executable program.

### REVEALS_DATASET_SCHEMA

签名：`REVEALS_DATASET_SCHEMA(observation: observation)`

The observation exposes structured schema-level information about a data source, such as configuration or subset names, field or column names, data types, or split definitions.

参数：

- `observation: observation`：The observation containing structured schema, field, or configuration information for a data source.

成立条件：

- The observation enumerates or describes structured schema elements of a data source, such as configuration names, column or feature names, types, or splits.
- The information is specific enough to identify the individual fields or configurations available.

排除条件：

- The observation is free-form prose documentation without field-level or configuration-level structure.
- The observation only reports that a dataset exists, its size, or its file listing without schema details.
- The observation contains only raw records of data values without any schema description.

### ESTABLISHES_COMPUTATION_SPECIFICATION

签名：`ESTABLISHES_COMPUTATION_SPECIFICATION(reasoning: reasoning)`

The reasoning resolves an ambiguous or under-specified task requirement by committing to one concrete interpretation and stating the concrete specification — data fields, filtering criteria, computation procedure, or required behavior — that implementation should follow.

参数：

- `reasoning: reasoning`：The reasoning text that interprets the task and fixes the specification to implement.

成立条件：

- The reasoning identifies an ambiguity or alternative plausible interpretations in the task requirements.
- The reasoning selects one concrete interpretation and states enough detail about the fields, filters, operations, or required behavior to guide implementation.

排除条件：

- The reasoning only restates the task, or gives a general plan without concrete criteria.
- The reasoning reports results or execution rather than specifying the computation.
- The reasoning mentions fields or operations without resolving any ambiguity or under-specification.
- The ambiguity concerns tool availability or environment state rather than requirement semantics.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(probe_action: action, assumption_reasoning: reasoning, probe_observation: observation)`

A targeted action empirically tests a specific assumption or ambiguity identified in prior reasoning, and the resulting observation provides evidence that resolves how that assumption affects the task.

参数：

- `probe_action: action`：The action performing the targeted empirical check.
- `assumption_reasoning: reasoning`：The reasoning explicitly identifying the assumption, ambiguity, or uncertainty to be tested.
- `probe_observation: observation`：The observation reporting the behavior relevant to the tested assumption.

成立条件：

- The assumption reasoning explicitly identifies an assumption or ambiguity whose truth could change the task result.
- The probe action is a focused check of that assumption, such as a small isolated test, diagnostic query, or controlled experiment, rather than the main computation.
- The probe observation reports behavior relevant to the assumption and supplies enough evidence to decide whether the assumption holds or how to interpret it.

排除条件：

- The action is the main computation or general exploration.
- No explicit assumption or uncertainty is identified in the reasoning.
- The probe result does not address the identified assumption.

### RESOLVES_TERM_AMBIGUITY_USING_REFERENCE

签名：`RESOLVES_TERM_AMBIGUITY_USING_REFERENCE(interpretation_reasoning: reasoning, reference_observation: observation, data_observation: observation)`

Reasoning resolves an underspecified or non-matching term from the task by combining a reference description with the category values actually observed in the data to select the concrete categories that the term denotes.

参数：

- `interpretation_reasoning: reasoning`：The reasoning that selects concrete categories as the meaning of the task term.
- `reference_observation: observation`：The observation supplying a taxonomy, grouping, or documentary description that relates observed categories to the term.
- `data_observation: observation`：The observation showing the category values actually present in the data.

成立条件：

- The data observation shows category labels or values that do not directly match the task term.
- The reference observation supplies a taxonomy, grouping, or documentary description relating the observed categories to the task term.
- The interpretation reasoning explicitly selects one or more observed categories as constituting the task term, using both the reference description and the observed values.

排除条件：

- The data already contains an exact matching category for the term.
- The mapping is asserted without documentary or other supporting evidence.
- The reasoning does not connect both the reference description and the observed values.
- The reasoning merely reports values without resolving the term.

### CROSS_VALIDATES_RESULT

签名：`CROSS_VALIDATES_RESULT(verification_action: action, original_result: observation, verification_result: observation)`

An independent verification action recomputes an already obtained result through a different data-access path or method, and the resulting observation reproduces the same value.

参数：

- `verification_action: action`：The action performing the independent recomputation.
- `original_result: observation`：The earlier observation reporting the originally computed value.
- `verification_result: observation`：The later observation reporting the independently recomputed value.

成立条件：

- The original result reports a computed value.
- The verification action uses an independent mechanism, such as a different library, data path, or algorithm, rather than repeating the same call.
- The verification result reports a value equal to the original result.

排除条件：

- The same procedure is repeated without an independent data-access path or method.
- The recomputed result differs from the original result.
- The verification only checks formatting or presence rather than reproducing the value.

### VERIFIES_ARTIFACT_BY_READBACK

签名：`VERIFIES_ARTIFACT_BY_READBACK(readback_action: action, artifact_content: observation)`

An action reads back a previously produced or written output artifact from its destination, and the resulting observation provides content, size, or checksum evidence consistent with the intended value, confirming that the artifact was persisted with the intended content.

参数：

- `readback_action: action`：The action that reads the stored output artifact.
- `artifact_content: observation`：The observation displaying the stored artifact's content or reporting size or checksum evidence.

成立条件：

- A prior action produced, wrote, or updated the output artifact in its destination.
- The readback action reads the stored artifact rather than recomputing or transforming the result.
- The resulting observation displays stored content, or reports a size or checksum, consistent with the intended output value, serving as confirmation that the intended result was persisted.

排除条件：

- The artifact was not previously produced or written to the destination.
- The action recomputes or transforms the result rather than reading stored content.
- The observation does not display content and provides no size or checksum evidence of the artifact.
- The observed content or evidence differs from the intended target value.

### IDENTIFIES_RETENTION_MECHANISM

签名：`IDENTIFIES_RETENTION_MECHANISM(reasoning: reasoning, retention_observation: observation)`

The reasoning explains why a target that should otherwise be absent remains present or reachable by attributing its continued availability to an identifiable retaining reference, log, cache, index, or equivalent persistence structure visible in an observation, and it selects a removal strategy aimed at that retaining mechanism.

参数：

- `reasoning: reasoning`：The agent text explaining continued retention and choosing a removal strategy.
- `retention_observation: observation`：The observation showing that the target remains present or reachable despite an apparent removal.

成立条件：

- retention_observation shows that the target remains present, reachable, or not reported as removed or dangling despite an apparent removal.
- The reasoning attributes continued availability to an identifiable reference, log, cache, index, or equivalent retention structure.
- The reasoning selects or proposes an operation that expires, disables, or purges that retaining mechanism.

排除条件：

- The reasoning only repeats a generic cleanup sequence without explaining retention.
- retention_observation already shows the target absent.
- The reasoning attributes retention vaguely without identifying an inspectable mechanism.

### ATTEMPTS_TO_ERASE_OBSERVED_ARTIFACT

签名：`ATTEMPTS_TO_ERASE_OBSERVED_ARTIFACT(erasure_action: action, exposure_observation: observation)`

The action performs deletion, expiration, pruning, or equivalent removal operations directed at target data — or at the object, reference, or structure retaining it — that a prior observation identified.

参数：

- `erasure_action: action`：The action attempting to delete, expire, or prune the target or its retaining structure.
- `exposure_observation: observation`：The prior observation identifying the target content, object, or retaining reference.

成立条件：

- exposure_observation identifies target content, an object containing it, or a reference retaining it.
- erasure_action deletes, expires, or prunes that object, reference, or containing structure.
- The action is directed at the observed target rather than being routine maintenance with no identified target.

排除条件：

- The action only inspects or verifies the target.
- The action removes files or history without evidence that they contain or retain the target.
- No prior observation identifies the target or its retaining structure.

### CONFIRMS_ERADICATION

签名：`CONFIRMS_ERADICATION(erasure_action: action, exposure_observation: observation, verification_observation: observation)`

An erasure action removes target data identified by an earlier observation, and a later verification observation establishes that the target is absent from the relevant searched scopes.

参数：

- `erasure_action: action`：The action removing the target or the structure retaining it.
- `exposure_observation: observation`：The earlier observation revealing the target content or retaining structure.
- `verification_observation: observation`：The later observation establishing that the target is absent.

成立条件：

- exposure_observation reveals target content or a structure retaining it.
- erasure_action deletes, expires, or prunes the target or retaining structure after that observation.
- verification_observation occurs after the erasure and reports the target not found across the relevant repository internals, revision history, and/or object storage, as applicable.
- The verification evidence shows no remaining searched object or reference containing the target.

排除条件：

- There is no erasure action or no subsequent verification observation.
- The verification finds the target or checks only an unrelated scope.
- The erasure action does not address the target identified by the exposure observation.

### VERIFIES_PRESERVATION_OF_UNRELATED_ARTIFACTS

签名：`VERIFIES_PRESERVATION_OF_UNRELATED_ARTIFACTS(reasoning: reasoning, verification_observation: observation)`

The reasoning uses a post-remediation observation to validate that artifacts unrelated to the target remain unchanged, by comparing their content, identifiers, or status with an earlier known state.

参数：

- `reasoning: reasoning`：The agent text validating that unrelated artifacts were preserved.
- `verification_observation: observation`：The post-remediation observation reporting content, identifiers, or status of non-target artifacts.

成立条件：

- verification_observation reports content, hashes, status, or identifiers of non-target artifacts after remediation.
- The reasoning explicitly compares that report with an earlier state or asserts identity and cleanliness of those artifacts.
- The preservation conclusion is tied to the reported evidence for those unrelated artifacts.

排除条件：

- Only target artifacts are examined.
- The reasoning assumes preservation without reported evidence from the observation.
- The observation predates the destructive or remediation action.

### PERFORMS_EXHAUSTIVE_UNIQUENESS_SEARCH

签名：`PERFORMS_EXHAUSTIVE_UNIQUENESS_SEARCH(search_action: action)`

The action enumerates the complete accessible object set, or an equivalent full corpus, and searches each item for the target pattern to determine whether the target occurs uniquely.

参数：

- `search_action: action`：The action enumerating objects or corpus items and searching them for the target.

成立条件：

- search_action enumerates all accessible objects, blobs, or corpus items rather than a sample.
- Each enumerated item is searched for the target pattern.
- The output associates occurrences with item identifiers or otherwise supports a uniqueness conclusion.

排除条件：

- The action searches only a single file, directory, or preselected subset.
- The action does not attempt to determine whether the target occurs more than once.
- Enumeration is incomplete so uniqueness cannot be established.

### PERFORMS_CROSS_SCOPE_ABSENCE_VERIFICATION

签名：`PERFORMS_CROSS_SCOPE_ABSENCE_VERIFICATION(verification_action: action)`

The action checks for a target across multiple independent storage scopes, such as working files, repository metadata, revision history, and object inventory, in order to confirm its absence rather than locate a present value.

参数：

- `verification_action: action`：The action checking multiple scopes for the target's absence.

成立条件：

- verification_action includes at least two independent searches or inspections for the target.
- The scopes cover different storage layers, histories, or metadata areas.
- The action is aimed at confirming absence rather than only locating a present target.

排除条件：

- The action performs a single grep or file check.
- The action checks only one storage layer.
- The action is not aimed at confirming absence.

### REPORTS_TARGET_ABSENT_ACROSS_SCOPES

签名：`REPORTS_TARGET_ABSENT_ACROSS_SCOPES(verification_observation: observation)`

The observation explicitly reports that the target was not found in multiple searched scopes and provides corroborating inventory or status evidence for absence.

参数：

- `verification_observation: observation`：The observation reporting not-found results and corroborating absence evidence.

成立条件：

- verification_observation contains explicit not-found results for at least two independent scopes.
- Corroborating evidence such as an object inventory, status, or remaining-content listing supports the absence claim.
- No execution error or ambiguity prevents interpreting the result as absence.

排除条件：

- Only one not-found result is reported.
- The command errored or output is ambiguous.
- The observation reports that the target is present.

### REPORTS_ENVIRONMENT_OR_ARTIFACT_STATE

签名：`REPORTS_ENVIRONMENT_OR_ARTIFACT_STATE(observation: observation)`

The observation enumerates concrete, factual state of the execution environment or of stored artifacts — such as directory contents, interpreter or library versions, installed packages, or retained/downloaded files with sizes — which can be used as operational ground truth.

参数：

- `observation: observation`：The tool result enumerating concrete environment or artifact facts.

成立条件：

- The observation content enumerates concrete facts such as file or directory names, version strings, installed packages, or retained assets, rather than only acknowledging an operation.
- The observation completes without an execution error that truncates or invalidates the enumeration.

排除条件：

- The observation returns an application response payload produced by a service endpoint.
- The observation reports an execution error or failure trace.
- The observation merely acknowledges that a write or other operation succeeded.
- The observation supplies schema-level definitions of a data source rather than environment or artifact state.

### CONFIRMS_EXTERNAL_REACHABILITY

签名：`CONFIRMS_EXTERNAL_REACHABILITY(action: action, observation: observation)`

A request contacts the running service through a host interface address other than the loopback address, and the resulting observation reports a successful response, establishing that the service is reachable beyond local-only access.

参数：

- `action: action`：The invocation that contacts the service through a non-loopback host interface address.
- `observation: observation`：The result of that request, indicating success or failure.

成立条件：

- The address targeted by the request is a host interface address other than localhost/127.0.0.1, such as a container or external interface address.
- The observation reports a successful response from the service at that address.

排除条件：

- The request targets localhost or 127.0.0.1.
- The request fails to reach the service, so external reachability is not confirmed.
- The evidence of availability is only a process listing, configuration value, or listening-socket entry rather than a successful remotely addressed request.

### ASSESSES_REQUIREMENTS_AS_SATISFIED

签名：`ASSESSES_REQUIREMENTS_AS_SATISFIED(reasoning: reasoning)`

The reasoning performs a final requirements assessment that maps multiple distinct requirements from the task specification to supporting evidence and concludes that all of them are satisfied.

参数：

- `reasoning: reasoning`：The agent text performing the final requirements assessment and declaring the requirements satisfied.

成立条件：

- The reasoning addresses multiple distinct requirements from the task specification.
- Each addressed requirement is marked as satisfied or verified, with reference to supporting evidence or observed behavior.
- The reasoning concludes that all requirements are fulfilled or declares the task complete.

排除条件：

- The reasoning reports only partial progress, unresolved issues, or remaining work.
- The reasoning lists or restates requirements without concluding that they are satisfied.
- The reasoning states a general completion claim without mapping individual requirements to supporting evidence.
