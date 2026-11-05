# 第 2 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：11–20
Prompt 版本：v0001
本批新增谓词：20
本批已有谓词修订：3
当前谓词总数：74

## 二、本批新增谓词

### ENACTS_DERIVED_CONSTRAINT

签名：`ENACTS_DERIVED_CONSTRAINT(constraint_reasoning: reasoning, action: action)`

The reasoning derives a necessary condition that must hold for the target system to function as required, and the action performs an operation that establishes that condition.

参数：

- `constraint_reasoning: reasoning`：The reasoning stating a necessary condition or implication required for the system to work correctly, derived from requirements or observed runtime facts.
- `action: action`：The recorded invocation that brings about the stated necessary condition.

成立条件：

- The reasoning states a necessary condition or implication that must hold for the target system to work correctly, derived from task requirements or observed runtime facts rather than merely asserted as a goal.
- The action performs an operation that establishes that condition, for example by adjusting ownership, permissions, or other required settings.

排除条件：

- The reasoning states only a general goal or desired outcome without a derived necessary condition.
- The action satisfies some requirement that the reasoning never expressed as a condition.
- The reasoning states the condition but no corresponding action establishes it.

### VERIFIES_CHANGE_EFFECT

签名：`VERIFIES_CHANGE_EFFECT(change_action: action, verification_observation: observation)`

An action applies or initiates a state change on a targeted object, and the observation reports the resulting state of that same object in a form that shows whether the intended effect of the change is present.

参数：

- `change_action: action`：The recorded invocation that applies or initiates the state change.
- `verification_observation: observation`：The observation reporting the post-change state of the targeted object.

成立条件：

- The action performs or initiates a state change on a targeted object, such as starting a service, writing a file, creating a resource, or altering configuration.
- The observation reports the resulting state of that same targeted object in a form from which the presence or absence of the intended effect can be read.

排除条件：

- The observation reports only pre-change state or output unrelated to the changed object.
- The action is a pure read that changes nothing.
- The observation reports that the intended effect of the change is absent.

### REMOVES_SUPERSEDED_ARTIFACTS_TO_RESOLVE_CONFLICT

签名：`REMOVES_SUPERSEDED_ARTIFACTS_TO_RESOLVE_CONFLICT(cleanup_action: action, conflict_reasoning: reasoning)`

The reasoning identifies a duplication or conflict in which redundant artifacts overlap or compete with an authoritative configuration that is to be preserved, and the action removes those redundant artifacts so that only the authoritative configuration remains in effect.

参数：

- `cleanup_action: action`：The action that deletes or disables the redundant or conflicting artifacts.
- `conflict_reasoning: reasoning`：The reasoning that identifies the duplication or conflict, designates the authoritative configuration to keep, and prescribes removal of the redundant artifacts.

成立条件：

- The reasoning identifies a duplication or conflict between redundant artifacts (typically those the agent itself created) and an authoritative configuration or artifact that should be preserved.
- The cleanup action removes or disables those specific redundant or conflicting artifacts.
- The authoritative configuration referenced in the reasoning is left in place and remains the operative one after the action.

排除条件：

- The action removes artifacts without any identified duplication or conflict, such as routine tidying of unrelated files.
- The action merely overwrites, patches, or reconfigures the offending artifact instead of removing or disabling it.
- The reasoning identifies the conflict but no corresponding removal action is performed.
- The removed artifacts are neither the agent's own redundant artifacts nor duplicates of a configuration that is being preserved.

### PLANS_WITH_FALLBACK

签名：`PLANS_WITH_FALLBACK(reasoning: reasoning)`

The reasoning states a primary course of action together with an explicit contingent alternative that will be used if the primary approach is unavailable, fails, or an expected enabling condition is not met, so both courses remain available rather than one being discarded.

参数：

- `reasoning: reasoning`：The agent text presenting the primary course of action and the contingent alternative held in reserve.

成立条件：

- The reasoning identifies a primary action or approach that the agent intends to attempt.
- The reasoning identifies at least one alternative action or approach explicitly conditioned on the primary approach failing, being unavailable, or its enabling condition not holding.
- Both the primary and the contingent alternative are retained as viable courses of action.

排除条件：

- The reasoning presents only a single course of action or an unconditional sequence of steps.
- The reasoning mentions alternatives without tying them to a contingency that triggers them.
- The reasoning weighs mutually exclusive candidates and selects one while abandoning the others, which is option selection rather than fallback planning.

### ANALYZES_EXTERNAL_VALIDATION_RISK

签名：`ANALYZES_EXTERNAL_VALIDATION_RISK(reasoning: reasoning)`

The reasoning models plausible procedures, assumptions, or edge cases of an external validator, test harness, or consumer of the deliverable, and identifies a specific condition under which the current or planned system state would fail that validation.

参数：

- `reasoning: reasoning`：The agent text reasoning about how an external validator might behave and where the current or planned state could fail it.

成立条件：

- The reasoning describes at least one plausible procedure, command sequence, assumption, or edge case that an external validator or consumer of the deliverable might exhibit.
- The reasoning identifies a concrete condition under which the current or planned system state would fail under that validation.
- The identified risk concerns externally imposed validation rather than the agent's own planned checks.

排除条件：

- The reasoning only plans the agent's own verification steps.
- The reasoning expresses generic concern or uncertainty without naming a validator behavior and a corresponding failure condition.
- No external validation or downstream consumer of the deliverable is under consideration.
- The reasoning only explains a failure that has already been observed rather than anticipating a possible validation outcome.

### SELECTS_UNDERTESTED_PATH_FOR_VERIFICATION

签名：`SELECTS_UNDERTESTED_PATH_FOR_VERIFICATION(selection_reasoning: reasoning)`

The reasoning identifies a specific behavior, path, or condition that prior verification did not exercise and proposes an additional check for it, explaining what that check would reveal about the implementation or requirements.

参数：

- `selection_reasoning: reasoning`：The reasoning identifying an unexercised behavior, path, or condition and proposing a check for it.

成立条件：

- The reasoning identifies a specific behavior, path, or condition that earlier verification did not exercise.
- The reasoning proposes an additional check directed at that unexercised behavior, path, or condition.
- The reasoning states what the proposed check would reveal or confirm about the implementation or requirements, such as whether update or replacement logic behaves differently from initial creation.
- The proposed check is treated as pending at the time of the reasoning rather than already performed and confirmed.

排除条件：

- The reasoning proposes repeating a check that was already performed and confirmed.
- The reasoning lists planned steps without identifying any specific untested behavior, path, or condition.
- The proposed work concerns cleanup, reporting, or modification rather than verification of behavior.
- No specific unexercised behavior, path, or condition is identified.

### MEASURES_OPERATION_LATENCY

签名：`MEASURES_OPERATION_LATENCY(timed_action: action)`

The action instruments a specific operation with timing markers and computes or reports the elapsed duration attributable to that operation, producing a quantified latency measurement.

参数：

- `timed_action: action`：The action that brackets a specific operation with timing markers and computes or reports its elapsed duration.

成立条件：

- The action records a time marker before and after a specific operation.
- The action computes or reports the elapsed duration attributable to that operation from those markers.
- The measured operation is identifiable as the interval between the timing markers.

排除条件：

- The action reports a timestamp or duration without bracketing any specific operation.
- The timing markers span multiple unrelated operations so the resulting value cannot be attributed to one operation.
- The action does not compute or report an elapsed duration.

### EVALUATES_RESULT_AGAINST_ACCEPTANCE_CRITERION

签名：`EVALUATES_RESULT_AGAINST_ACCEPTANCE_CRITERION(evaluation_reasoning: reasoning, measured_observation: observation)`

The reasoning compares a concrete value, measurement, property, or outcome reported in the observation against a stated requirement, threshold, or expected property and judges whether that criterion is satisfied.

参数：

- `evaluation_reasoning: reasoning`：The reasoning that states the requirement, threshold, or expected property and renders a compliance judgment.
- `measured_observation: observation`：The observation supplying the concrete value, measurement, property, or outcome being judged.

成立条件：

- The observation contains an identifiable concrete value, measurement, property, or outcome.
- The reasoning states a requirement, threshold, or expected property and explicitly relates the observed value, measurement, property, or outcome to it.
- The reasoning concludes that the criterion is met or not met.

排除条件：

- The reasoning cites the observed result without comparing it to any stated requirement, threshold, or expected property.
- The comparison is asserted without an observed value or property to compare.
- The observation lacks the value, measurement, property, or outcome that the requirement concerns.
- The reasoning only restates the observation without rendering a compliance judgment.

### DECLARES_TASK_COMPLETION_WITH_REQUIREMENT_MAPPING

签名：`DECLARES_TASK_COMPLETION_WITH_REQUIREMENT_MAPPING(completion_reasoning: reasoning)`

The reasoning explicitly claims that the overall task is complete and itemizes multiple stated requirements alongside the outcomes or evidence that satisfy them, forming a final accountability record rather than an interim status update.

参数：

- `completion_reasoning: reasoning`：The reasoning containing the completion claim and the requirement-to-outcome or requirement-to-evidence mapping.

成立条件：

- The reasoning explicitly claims that the overall task is complete.
- The reasoning enumerates multiple requirements taken from the task statement or specification.
- Each enumerated requirement is associated with a satisfied outcome or identifiable evidence.
- No requirement is presented as satisfied while also being described as unresolved.

排除条件：

- The reasoning is an interim status report without a completion claim.
- The reasoning asserts completion without mapping requirements to outcomes or evidence.
- The reasoning lists some requirements as unresolved while still claiming full completion.
- The reasoning maps only a single requirement rather than multiple stated requirements.

### INTERPRETS_SPECIFICATION_CONSTRAINT

签名：`INTERPRETS_SPECIFICATION_CONSTRAINT(reasoning: reasoning)`

The reasoning interprets a stated requirement, schema, contract, or acceptance condition and derives a concrete implementation, validation, or response decision from it, including committing to how an ambiguous requirement should be applied.

参数：

- `reasoning: reasoning`：The agent text interpreting a stated requirement or acceptance condition and deriving a concrete implementation or validation decision from it.

成立条件：

- The reasoning explicitly references a stated requirement, schema, contract, or acceptance condition.
- The reasoning derives a concrete implementation, validation, response, or formatting decision from that requirement rather than merely restating it.

排除条件：

- The reasoning only restates or paraphrases a requirement without deriving any implementation or validation decision.
- The reasoning makes an implementation choice without connecting it to a stated requirement or acceptance condition.
- The reasoning evaluates observed results against a requirement instead of deciding how the requirement should be implemented or enforced.

### SELECTS_ALTERNATIVE_TOOL_AFTER_UNAVAILABILITY

签名：`SELECTS_ALTERNATIVE_TOOL_AFTER_UNAVAILABILITY(unavailability_observation: observation, adaptation_reasoning: reasoning, alternative_action: action)`

An observation reports that an intended tool, command, capability, or method is unavailable or unusable, and the reasoning selects a functionally equivalent alternative approach that a subsequent action then invokes in pursuit of the same objective.

参数：

- `unavailability_observation: observation`：The observation reporting that the intended tool, command, capability, or method is missing, not found, or otherwise unavailable.
- `adaptation_reasoning: reasoning`：The reasoning selecting a functionally equivalent alternative tool or method for the same objective.
- `alternative_action: action`：The invocation that uses the selected alternative tool or method.

成立条件：

- The observation reports that an intended tool, command, capability, or method is missing, not found, or otherwise unavailable.
- The reasoning explicitly selects a different tool, command, or method intended to accomplish the same objective.
- The alternative action invokes that selected alternative rather than repeating the unavailable one.

排除条件：

- The observed failure is unrelated to tool or method availability, such as an incorrect argument, a defect in the produced artifact, or a rejected input.
- The reasoning only acknowledges the unavailability without selecting an alternative.
- The alternative action is unrelated to the unavailable tool or does not serve the same objective.
- The selection contrasts candidate approaches before any unavailability is observed, without a specific unusable tool motivating the switch.

### ASSESSES_PERSISTENCE_BY_DEPLOYMENT_MECHANISM

签名：`ASSESSES_PERSISTENCE_BY_DEPLOYMENT_MECHANISM(persistence_reasoning: reasoning)`

The reasoning evaluates whether a launched process or started service will survive beyond the current session or command context, justifying that assessment from properties of the deployment mechanism (such as detachment, signal handling, or output redirection) rather than from the mere fact that the process is currently executing.

参数：

- `persistence_reasoning: reasoning`：The reasoning that raises the post-session survival question for a launched process or service and justifies its answer from deployment mechanics.

成立条件：

- The reasoning identifies a persistence or lifecycle concern for a launched process or started service, such as whether it survives session termination.
- The reasoning explains why the process should or should not survive by appealing to a deployment mechanism, such as detachment, ignore-signal handling, backgrounding, or output redirection.
- The persistence conclusion is derived from that mechanism rather than from merely observing that the process is currently running.

排除条件：

- The reasoning only states that the process is currently running or reachable.
- No durability or post-session survival question is considered.
- The reasoning asserts persistence without any mechanism-based justification.
- The reasoning merely plans to guard against a failure mode without assessing whether the deployed process will persist.

### REPORTS_EXECUTION_ERROR

签名：`REPORTS_EXECUTION_ERROR(observation: observation)`

The observation reports that an attempted operation did not succeed, conveying an error status, failure message, missing-tool or missing-resource fault, or rejected-request indication rather than a valid result of the requested operation.

参数：

- `observation: observation`：The observation conveying non-success of the attempted operation.

成立条件：

- The observation carries an identifiable non-success indication, such as an explicit error flag, an error or failure message, a missing command or resource fault, or a rejected request.
- The indication concerns the operation that was attempted, so that the attempt is not confirmed as successful.

排除条件：

- The observation reports successful completion or a normal result value of the requested operation.
- The observation reports a negative fact about the domain state, such as an empty directory, an absent key, or a missing artifact, while the operation itself succeeded.
- The observation reports an outcome of a diagnostic check whose result is a valid, usable answer to the question posed.

### JUDGES_PRIOR_RESULT_INCONCLUSIVE

签名：`JUDGES_PRIOR_RESULT_INCONCLUSIVE(reasoning: reasoning, observation: observation)`

The reasoning assesses a prior observation as insufficient, ambiguous, or otherwise uninformative for establishing the targeted state, because its reported content is empty, errored, or cannot discriminate between the possible answers to the question posed.

参数：

- `reasoning: reasoning`：The reasoning that evaluates the prior observation as inconclusive for the targeted state.
- `observation: observation`：The prior observation whose result is judged insufficient, ambiguous, or uninformative.

成立条件：

- The reasoning refers to an earlier observation and characterizes its content as empty, ambiguous, failed, or otherwise unable to establish the targeted state.
- The reasoning explains why that result does not settle the question, for example by noting that the content cannot distinguish between the possible conditions or that a further, different check is required.

排除条件：

- The reasoning treats the prior observation as definitive confirmation or disconfirmation of the targeted state.
- The reasoning does not refer to any prior observation.
- The observation is unrelated to the state the reasoning is trying to establish.

### DISAMBIGUATES_FALSE_POSITIVE_MATCH

签名：`DISAMBIGUATES_FALSE_POSITIVE_MATCH(reasoning: reasoning, observation: observation)`

The reasoning explains that an apparent match or candidate present in an observation does not satisfy the sought condition because the matching content originates from incidental, contextual, or unrelated material, and thereby distinguishes it from a genuine match.

参数：

- `reasoning: reasoning`：The reasoning that explains why the apparent match is a false positive.
- `observation: observation`：The observation containing the apparent match or candidate.

成立条件：

- The observation contains at least one apparent candidate match for a sought condition or target.
- The reasoning explains why that candidate does not actually satisfy the condition, citing the incidental, contextual, or unrelated origin of the matching content.
- The reasoning distinguishes the false positive from a genuine match, or concludes that no genuine match exists among the apparent candidates.

排除条件：

- The reasoning accepts the apparent match as genuine without explanation.
- The reasoning does not identify any apparent match in the observation.
- The reasoning merely states that no match is present without explaining why a candidate was misleading.
- The reasoning dismisses the candidate without explaining where the matching content came from.

### CHECKS_REQUIREMENTS_AGAINST_OBSERVED_STATE

签名：`CHECKS_REQUIREMENTS_AGAINST_OBSERVED_STATE(requirement_reasoning: reasoning, evidence_observations: observation[])`

The reasoning enumerates multiple distinct requirements, deliverables, or acceptance conditions and treats facts drawn collectively from observations as evidence of whether each enumerated item is satisfied.

参数：

- `requirement_reasoning: reasoning`：The reasoning that enumerates requirements or deliverables and assesses them against observed facts.
- `evidence_observations: observation[]`：The observations that collectively supply facts corresponding to the enumerated requirements; support is collective.

成立条件：

- The reasoning identifies or enumerates multiple distinct requirements, deliverables, or acceptance conditions.
- The evidence observations collectively report facts that correspond to those enumerated requirements.
- The reasoning maps or assesses those observed facts against the requirements rather than merely restating the task statement.

排除条件：

- The reasoning lists requirements without relating them to observed facts.
- The observations do not contain facts that address the enumerated requirements.
- Only a single requirement is assessed, so no multi-requirement evidence mapping is present.
- The reasoning restates the task requirements without any observed evidence for their satisfaction.

### REVISES_BELIEF_WITH_NEW_EVIDENCE

签名：`REVISES_BELIEF_WITH_NEW_EVIDENCE(revision_reasoning: reasoning, evidence_observation: observation)`

The reasoning explicitly corrects or updates an earlier belief, interpretation, or hypothesis in response to identifiable new evidence reported by an observation, and states the revised belief.

参数：

- `revision_reasoning: reasoning`：The reasoning text that supersedes a prior belief and states the revised belief or interpretation.
- `evidence_observation: observation`：The observation supplying the new evidence that motivates the revision.

成立条件：

- The reasoning refers to a prior belief, hypothesis, or provisional interpretation and presents it as superseded or corrected.
- The reasoning changes or corrects that belief in response to identifiable content of the observation.
- The reasoning states what the revised belief is.

排除条件：

- The reasoning merely repeats the observation without referencing a prior belief.
- The observation is unrelated to the belief being revised.
- No prior belief or provisional interpretation is identifiable in the reasoning.
- The reasoning only revises a planned course of action rather than a belief, hypothesis, or interpretation.

### IDENTIFIES_DATA_AMBIGUITY

签名：`IDENTIFIES_DATA_AMBIGUITY(reasoning: reasoning)`

The reasoning recognizes that a token, field value, or record in the data being processed can occupy more than one semantic role or context, creating a risk that a naive extraction, count, or classification would treat an unintended occurrence as the intended one.

参数：

- `reasoning: reasoning`：The agent text identifying that a value can play competing roles in the data and that misclassification is a risk.

成立条件：

- The reasoning points to a specific token, value, or record type that can appear in more than one role or context within the data.
- The reasoning states or clearly implies that confusing those occurrences would produce an incorrect extraction, count, or classification.
- The reasoning distinguishes the intended structured occurrence from the competing occurrence of the same token or value.

排除条件：

- The reasoning merely describes the data format without noting any competing role for a token or value.
- The reasoning selects a parsing or extraction rule without identifying any token that could be confused with another role.
- The ambiguity concerns the wording of the task or requirements rather than the content of the data.

### OBSERVATION_CONTRADICTS_EXPECTATION

签名：`OBSERVATION_CONTRADICTS_EXPECTATION(expectation_reasoning: reasoning, contradicting_observation: observation)`

The reasoning states, presupposes, or clearly implies a specific property, condition, format, or outcome that should hold, and the observation contains identifiable content showing that this expected condition does not hold.

参数：

- `expectation_reasoning: reasoning`：The agent text stating, presupposing, or clearly implying the property, condition, format, or outcome that should hold.
- `contradicting_observation: observation`：The observation containing content that shows the stated or implied expectation is violated.

成立条件：

- The reasoning states, presupposes, or clearly implies a specific expected property, condition, format, or outcome for the artifact, result, or state under consideration.
- The observation contains identifiable content showing that the expected property, condition, format, or outcome does not hold.

排除条件：

- The observation is consistent with, or confirms, the stated or implied expectation.
- The reasoning only registers uncertainty about the outcome and states no condition that is expected to hold.
- The difference between the observation and the expectation is not identifiable or bears on something other than the stated expectation.
- The reasoning draws its own explicit adverse judgment from the observation, which is a separate evaluation mechanism rather than an expectation-content contradiction.

### ASSERTS_TASK_COMPLETION

签名：`ASSERTS_TASK_COMPLETION(reasoning: reasoning)`

The reasoning makes a final claim that the overall task and its required deliverable have been completed, presenting completion as the concluded final state rather than as an intention, a plan, or an intermediate progress report.

参数：

- `reasoning: reasoning`：The reasoning node containing the final completion claim.

成立条件：

- The reasoning explicitly declares the task, or its required deliverable, complete, done, or finally achieved.
- The claim concerns the overall task outcome or its acceptance conditions rather than a single intermediate subtask.
- The statement is presented as a conclusion about the final state rather than as an intended future action or a progress report.

排除条件：

- The reasoning only describes intended future work, cleanup, or partial progress.
- The reasoning expresses unresolved uncertainty about whether the requirements have been met.
- The reasoning reports completion of a subtask without claiming overall task completion.
- The reasoning merely restates the task requirements without asserting that they have been satisfied.

## 三、本批已有谓词修订

### IS_PLAN → IS_PLAN

Window：xhigh__git-multibranch__window_0001

修订前：

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses at least one intended future action or sequence of actions to be taken in service of the task.

参数：

- `reasoning: reasoning`：The agent text expressing an intended future action or plan.

成立条件：

- The reasoning explicitly identifies at least one operation or sequence of operations that the agent intends to perform later.
- The intended action is presented as something to be done, not merely as a completed observation or factual statement.

排除条件：

- The reasoning only reports actions that have already been completed.
- The reasoning states a fact or diagnosis without expressing any intended future action.

修订后：

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses at least one intended future action or sequence of actions to be taken in service of the task.

参数：

- `reasoning: reasoning`：The agent text expressing an intended future action or plan.

成立条件：

- The reasoning explicitly identifies at least one operation or sequence of operations that the agent intends to perform later.
- The intended action is presented as something to be done, not merely as a completed observation or factual statement.

排除条件：

- The reasoning only reports actions that have already been completed.
- The reasoning states a fact or diagnosis without expressing any intended future action.
- The reasoning only restates the task requirements without committing to any operation the agent will itself carry out.

### DIAGNOSES_ACTION_FAILURE_FROM_ERROR → DIAGNOSES_ACTION_FAILURE_FROM_ERROR

Window：xhigh__git-multibranch__window_0004

修订前：

### DIAGNOSES_ACTION_FAILURE_FROM_ERROR

签名：`DIAGNOSES_ACTION_FAILURE_FROM_ERROR(diagnosis_reasoning: reasoning, error_observation: observation)`

The reasoning interprets an error or non-success result reported by an observation and identifies the cause or the condition that a corrected attempt must satisfy.

参数：

- `diagnosis_reasoning: reasoning`：The reasoning that interprets the failure and identifies its cause or required correction.
- `error_observation: observation`：The observation reporting the error or non-success result.

成立条件：

- The observation reports an error, nonzero exit, or otherwise unsuccessful result from a prior action.
- The reasoning identifies a cause, misunderstood condition, or requirement for a corrected attempt.

排除条件：

- The reasoning merely repeats the error message without interpreting its cause or implications.
- The reasoning retries the same operation without identifying any corrective condition.
- The observation does not report an error or failure.

修订后：

### DIAGNOSES_ACTION_FAILURE_FROM_ERROR

签名：`DIAGNOSES_ACTION_FAILURE_FROM_ERROR(diagnosis_reasoning: reasoning, error_observation: observation)`

The reasoning interprets an error or non-success result reported by an observation and identifies a specific cause or the condition that a corrected attempt must satisfy, where the identified cause is tied to the details of the reported failure rather than merely restating the error or generically attributing it to the target functionality.

参数：

- `diagnosis_reasoning: reasoning`：The reasoning that interprets the failure and identifies its specific cause or required correction.
- `error_observation: observation`：The observation reporting the error or non-success result.

成立条件：

- The observation reports an error, nonzero exit, or otherwise unsuccessful result from a prior action.
- The reasoning identifies a cause, misunderstood condition, or requirement for a corrected attempt.
- The identified cause or requirement is consistent with the specific details of the reported error rather than a generic assertion that the target functionality is broken.

排除条件：

- The reasoning merely repeats the error message without interpreting its cause or implications.
- The reasoning retries the same operation without identifying any corrective condition.
- The reasoning attributes the failure to the target functionality without tying that attribution to the observed error details.
- The observation does not report an error or failure.

### GROUNDS_CONCLUSION_IN_OBSERVATION → GROUNDS_CONCLUSION_IN_OBSERVATION

Window：xhigh__kv-store-grpc__window_0001

修订前：

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(concluding_reasoning: reasoning, evidential_observation: observation)`

The reasoning draws a conclusion about the system, environment, or task state using identifiable content of the observation as supporting evidence.

参数：

- `concluding_reasoning: reasoning`：The reasoning that states the evidence-based conclusion.
- `evidential_observation: observation`：The observation supplying the content that supports the conclusion.

成立条件：

- The reasoning asserts a conclusion about the state, capability, or composition of the environment or artifacts.
- Specific content of the observation (reported items, absent items, versions, statuses, fetched output) supports that conclusion.

排除条件：

- The reasoning merely restates or paraphrases the observation without drawing an inference from it.
- The observation is unrelated to the stated conclusion or provides no identifiable support.

修订后：

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(concluding_reasoning: reasoning, evidential_observation: observation)`

The reasoning draws a conclusion, interpretation, or generalized finding about the system, environment, artifacts, or task situation using identifiable content of the observation as supporting evidence.

参数：

- `concluding_reasoning: reasoning`：The reasoning that states the evidence-based conclusion.
- `evidential_observation: observation`：The observation supplying the content that supports the conclusion.

成立条件：

- The reasoning states a conclusion, interpretation, or generalized finding that goes beyond merely restating the observation.
- Specific content of the observation (reported items, absent items, versions, statuses, listed or fetched output) is identifiable as the basis for that conclusion.

排除条件：

- The reasoning merely restates or paraphrases the observation without drawing an inference from it.
- The observation is unrelated to the stated conclusion or provides no identifiable support.
- The conclusion is reached solely from prior knowledge or from the task instructions, with the observation contributing no identifiable evidential support.

## 四、当前完整 Registry

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses at least one intended future action or sequence of actions to be taken in service of the task.

参数：

- `reasoning: reasoning`：The agent text expressing an intended future action or plan.

成立条件：

- The reasoning explicitly identifies at least one operation or sequence of operations that the agent intends to perform later.
- The intended action is presented as something to be done, not merely as a completed observation or factual statement.

排除条件：

- The reasoning only reports actions that have already been completed.
- The reasoning states a fact or diagnosis without expressing any intended future action.
- The reasoning only restates the task requirements without committing to any operation the agent will itself carry out.

### ACTION_IMPLEMENTS_PLANNED_STEP

签名：`ACTION_IMPLEMENTS_PLANNED_STEP(action: action, plan_reasoning: reasoning)`

A recorded action carries out an operation that a reasoning node explicitly proposed as a future step, with matching task purpose rather than merely topical or temporal adjacency.

参数：

- `action: action`：The recorded tool invocation that performs the step.
- `plan_reasoning: reasoning`：The reasoning node that proposes the future operation.

成立条件：

- The plan_reasoning expresses an intended future operation or set of operations.
- The action performs an operation consistent with the purpose and target of the proposed step.

排除条件：

- The reasoning only describes past or completed actions.
- The action is unrelated to the proposed step or serves a different purpose.
- The connection is based only on temporal adjacency without matching intent.

### DIAGNOSES_OBSERVED_ARTIFACT_DEFECT

签名：`DIAGNOSES_OBSERVED_ARTIFACT_DEFECT(diagnosis_reasoning: reasoning, artifact_observation: observation)`

The reasoning interprets content of an artifact exposed in an observation and identifies a specific missing, incomplete, or erroneous element that must be repaired.

参数：

- `diagnosis_reasoning: reasoning`：The reasoning that identifies the artifact defect or incompleteness.
- `artifact_observation: observation`：The observation exposing the artifact content being diagnosed.

成立条件：

- The observation exposes identifiable content of an artifact.
- The reasoning identifies a specific defect, gap, or incomplete element in that artifact relative to the intended requirement.

排除条件：

- The reasoning merely repeats or paraphrases the artifact content without identifying a defect.
- No specific missing, incomplete, or erroneous element is identified.
- The observation does not expose artifact content relevant to the diagnosis.

### PROPOSES_CONCRETE_REMEDIATION

签名：`PROPOSES_CONCRETE_REMEDIATION(remediation_reasoning: reasoning)`

The reasoning specifies a concrete correction, completion, or remediation for an identified defect, gap, or requirement, including replacement content or steps intended to make the target satisfy the requirement.

参数：

- `remediation_reasoning: reasoning`：The reasoning containing the proposed concrete remediation or completion.

成立条件：

- The reasoning identifies at least one concrete change, replacement, or added step intended to repair, complete, or remedy an identified defect, gap, or unmet requirement.
- The proposed remediation is tied to an identified defect, gap, or requirement rather than being a generic intention to fix something.

排除条件：

- The reasoning only identifies a defect without proposing how to repair or complete it.
- The reasoning expresses only a generic intention to fix or improve without concrete content or steps.
- The proposed change is unrelated to the identified defect or requirement.

### PROBES_CAPABILITY_AVAILABILITY

签名：`PROBES_CAPABILITY_AVAILABILITY(probe_action: action, probe_observation: observation)`

An action probes the execution environment for the availability, identity, or version of a capability or resource required for the task, and its observation reports capability evidence.

参数：

- `probe_action: action`：The diagnostic action that queries the environment for capability or resource availability.
- `probe_observation: observation`：The observation reporting the presence, absence, availability, identity, or version of the queried capability or resource.

成立条件：

- The action is a diagnostic query about a capability or resource relevant to the task.
- The observation reports capability evidence such as presence, absence, availability, identity, or version of the queried capability or resource.

排除条件：

- The action performs the primary task rather than checking capability or resource availability.
- The observation does not report any information about capability availability, identity, or version.
- The probe is unrelated to a capability or resource required by the task.

### IMPLEMENTS_SPECIFIED_CHANGE

签名：`IMPLEMENTS_SPECIFIED_CHANGE(change_action: action, change_reasoning: reasoning, application_observation: observation)`

An action applies concrete content, settings, or corrections that a reasoning node specified as intended, writing or applying them to the relevant target, and the observation reports that the application succeeded.

参数：

- `change_action: action`：The action that writes or applies the specified content, settings, or correction.
- `change_reasoning: reasoning`：The reasoning specifying the intended content, settings, target change, or correction.
- `application_observation: observation`：The observation reporting whether the specified change was successfully applied.

成立条件：

- The reasoning specifies intended content, settings, a target change, or a correction to be put in place.
- The action applies content or changes corresponding to that stated intent to the relevant target.
- The observation reports successful creation, writing, modification, or application of that change.

排除条件：

- The action does not implement the content or change described in the reasoning.
- The observation reports failure, an error, or only an attempt without confirming the write or application.
- The reasoning only discusses a change without stating an intended specification or correction.

### PRODUCES_EXPECTED_DERIVED_OUTPUT

签名：`PRODUCES_EXPECTED_DERIVED_OUTPUT(transformation_action: action, generation_observation: observation)`

An action invokes a transformation, build, compilation, or generation step on a source input, and its observation provides evidence that the expected derived artifact or output was generated.

参数：

- `transformation_action: action`：The action that runs the transformation, build, compilation, or generation process.
- `generation_observation: observation`：The observation reporting generation or existence of the expected derived output.

成立条件：

- The action invokes a transformation, build, compilation, or equivalent generation step on a source input.
- The observation provides evidence that the expected derived artifact or output was produced or exists after the step.

排除条件：

- The action only inspects files or inputs without invoking a transformation or generation step.
- The observation does not show that the expected derived artifact or output was generated.
- The transformation or generation reports an error preventing output production.

### DIAGNOSES_ACTION_FAILURE_FROM_ERROR

签名：`DIAGNOSES_ACTION_FAILURE_FROM_ERROR(diagnosis_reasoning: reasoning, error_observation: observation)`

The reasoning interprets an error or non-success result reported by an observation and identifies a specific cause or the condition that a corrected attempt must satisfy, where the identified cause is tied to the details of the reported failure rather than merely restating the error or generically attributing it to the target functionality.

参数：

- `diagnosis_reasoning: reasoning`：The reasoning that interprets the failure and identifies its specific cause or required correction.
- `error_observation: observation`：The observation reporting the error or non-success result.

成立条件：

- The observation reports an error, nonzero exit, or otherwise unsuccessful result from a prior action.
- The reasoning identifies a cause, misunderstood condition, or requirement for a corrected attempt.
- The identified cause or requirement is consistent with the specific details of the reported error rather than a generic assertion that the target functionality is broken.

排除条件：

- The reasoning merely repeats the error message without interpreting its cause or implications.
- The reasoning retries the same operation without identifying any corrective condition.
- The reasoning attributes the failure to the target functionality without tying that attribution to the observed error details.
- The observation does not report an error or failure.

### CORRECTS_FAILED_ACTION_WITH_DIAGNOSED_REVISION

签名：`CORRECTS_FAILED_ACTION_WITH_DIAGNOSED_REVISION(failed_action: action, error_observation: observation, correction_reasoning: reasoning, corrective_action: action)`

A subsequent action revises an earlier failed operation in accordance with an explicit diagnosis of the failure, rather than repeating the same operation unchanged.

参数：

- `failed_action: action`：The earlier action that produced the error result.
- `error_observation: observation`：The observation reporting the error from the failed action.
- `correction_reasoning: reasoning`：The reasoning that diagnoses the failure and indicates the needed revision.
- `corrective_action: action`：The subsequent action that implements the revised approach.

成立条件：

- The failed_action is associated with an error_observation reporting failure.
- The correction_reasoning identifies a cause or required change in approach.
- The corrective_action changes a relevant parameter, command, or method to address the diagnosed failure while pursuing the same goal.

排除条件：

- The subsequent action repeats the failed action identically without revision.
- The corrective action is unrelated to the diagnosed failure or targets a different goal.
- No error observation or explicit diagnosis supports the revision.

### CONCLUDES_TASK_SUCCESS_FROM_ACCUMULATED_EVIDENCE

签名：`CONCLUDES_TASK_SUCCESS_FROM_ACCUMULATED_EVIDENCE(conclusion_reasoning: reasoning, supporting_observations: observation[])`

The reasoning declares the task successfully completed and supports that declaration by referring to one or more observed verification outcomes rather than only restating the plan or action sequence.

参数：

- `conclusion_reasoning: reasoning`：The final reasoning that declares completion and cites verification evidence.
- `supporting_observations: observation[]`：The observations collectively supplying outcome evidence for the completion claim.

成立条件：

- The conclusion_reasoning asserts that the task has been successfully completed.
- The reasoning refers to or summarizes at least one observed outcome, such as a produced artifact or confirmed content.
- The supporting_observations collectively contain verification evidence rather than only action acknowledgments or plans.

排除条件：

- The reasoning merely restates plans or intermediate actions without asserting completion.
- The success assertion is not supported by any observed outcome evidence.
- The cited observations are unrelated to the claimed completion.

### EVALUATES_ALTERNATIVES

签名：`EVALUATES_ALTERNATIVES(deliberating_reasoning: reasoning)`

The reasoning contrasts two or more candidate approaches that could serve the same purpose and settles on one of them on the basis of an explicit comparative rationale.

参数：

- `deliberating_reasoning: reasoning`：The reasoning that contrasts candidate approaches and justifies the selected one.

成立条件：

- The reasoning names at least two candidate approaches, tools, or configuration choices that could serve the same purpose.
- The reasoning states a comparative rationale (robustness, availability, compatibility, convenience, simplicity) that favors the selected option over the alternative(s).

排除条件：

- The reasoning describes only a single approach without contrasting it against another.
- The reasoning merely lists planned steps without weighing options against each other.
- Another option is mentioned only in passing without any selection between the options being made.

### IS_STATE_PROBE

签名：`IS_STATE_PROBE(probe_action: action)`

The action is a read-only inspection of system, environment, or artifact state carried out to obtain information, without altering that state.

参数：

- `probe_action: action`：The action that inspects rather than modifies system or artifact state.

成立条件：

- The action consists of informational query or inspection operations, such as listing directories or processes, reading or dumping configuration, or querying package, user, or service state.
- The action's own description or command composition shows an informational purpose and contains no persistent modification of the inspected state.

排除条件：

- The action installs, creates, deletes, or reconfigures resources.
- An inspection command appears only incidentally inside an action whose purpose is a persistent change.
- The action executes a change and merely reports its own output.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(probe_action: action, assumption_reasoning: reasoning, probe_observation: observation)`

A targeted action is undertaken to discriminate a specific uncertainty or tentative assumption stated in reasoning about the environment, resources, tooling, data, or task requirements, and its observation supplies evidence bearing on that assumption.

参数：

- `probe_action: action`：The action performing the targeted test or inspection.
- `assumption_reasoning: reasoning`：The reasoning stating the uncertainty or tentative assumption being tested.
- `probe_observation: observation`：The observation whose content addresses the stated uncertainty.

成立条件：

- The reasoning explicitly formulates a specific uncertainty or tentative assumption whose truth would affect the result, procedure, or plan.
- The action is chosen so that its result would distinguish between the assumption holding and not holding.
- The observation contains content interpretable as evidence for or against the stated assumption.

排除条件：

- No identifiable assumption or uncertainty motivates the inspection.
- The action inspects something unrelated to the stated assumption.
- The observation does not address the assumption being tested.
- The action merely repeats an earlier operation without any assumption being formulated.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(concluding_reasoning: reasoning, evidential_observation: observation)`

The reasoning draws a conclusion, interpretation, or generalized finding about the system, environment, artifacts, or task situation using identifiable content of the observation as supporting evidence.

参数：

- `concluding_reasoning: reasoning`：The reasoning that states the evidence-based conclusion.
- `evidential_observation: observation`：The observation supplying the content that supports the conclusion.

成立条件：

- The reasoning states a conclusion, interpretation, or generalized finding that goes beyond merely restating the observation.
- Specific content of the observation (reported items, absent items, versions, statuses, listed or fetched output) is identifiable as the basis for that conclusion.

排除条件：

- The reasoning merely restates or paraphrases the observation without drawing an inference from it.
- The observation is unrelated to the stated conclusion or provides no identifiable support.
- The conclusion is reached solely from prior knowledge or from the task instructions, with the observation contributing no identifiable evidential support.

### ADAPTS_PLAN_TO_OBSERVED_STATE

签名：`ADAPTS_PLAN_TO_OBSERVED_STATE(revised_plan_reasoning: reasoning, state_revealing_observation: observation)`

The reasoning revises the intended course of action in response to a state revealed by the observation that departs from the assumptions of the earlier plan or that constrains the available options.

参数：

- `revised_plan_reasoning: reasoning`：The reasoning that sets out the adjusted course of action.
- `state_revealing_observation: observation`：The observation that reveals the state prompting the adjustment.

成立条件：

- The observation reports a state that departs from the assumptions of the earlier course of action or removes options from it.
- The reasoning explicitly derives a different set of subsequent steps as a consequence of that observed state.

排除条件：

- The reasoning repeats the previous plan unchanged after the observation.
- The reasoning records the observed state as a fact without altering what it intends to do next.
- The adjustment is only a reaction to an error from an attempted action that is handled as failure diagnosis and correction.

### MITIGATES_ANTICIPATED_FAILURE

签名：`MITIGATES_ANTICIPATED_FAILURE(safeguard_action: action, risk_reasoning: reasoning)`

The reasoning anticipates a specific failure mode that could prevent successful completion, and the action implements a measure aimed at preventing or neutralizing that failure before it occurs.

参数：

- `safeguard_action: action`：The action that implements the preventive measure.
- `risk_reasoning: reasoning`：The reasoning that identifies the failure mode and motivates the safeguard.

成立条件：

- The reasoning names a concrete failure mode or pitfall that could block the goal or invalidate the result.
- The action contains a measure whose stated or evident purpose is to prevent or neutralize that specific failure mode.

排除条件：

- The reasoning names no failure mode, so the measure cannot be tied to a risk.
- The action is ordinary setup work with no identifiable correspondence to the described failure mode.
- The safeguard is only proposed in reasoning and no corresponding action is performed.

### VALIDATES_PRECONDITION_BEFORE_DEPENDENT_ACTION

签名：`VALIDATES_PRECONDITION_BEFORE_DEPENDENT_ACTION(guarded_action: action)`

The action validates a precondition, configuration, or artifact for correctness and performs a dependent activation or use only after that validation succeeds, within one ordered guarded sequence.

参数：

- `guarded_action: action`：The action that runs the validation check and the dependent activation or use in a single guarded sequence.

成立条件：

- The action invokes a syntax, integrity, or validity check on a precondition, configuration, or artifact that is about to be used or activated.
- The dependent activation or use is sequenced after the check and is conditioned on the check succeeding.

排除条件：

- The action performs the dependent activation or use without any preceding validation of the precondition or artifact.
- A validation command is run in isolation long after the dependent action has already been performed.
- The dependent action proceeds regardless of the validation outcome.

### VERIFIES_EXPECTED_OUTCOME

签名：`VERIFIES_EXPECTED_OUTCOME(expectation_reasoning: reasoning, check_action: action, result_observation: observation)`

An action performs an operation or check directed at a specific behavior, output, content, result, resulting state, or constraint that reasoning identified as expected, and the observation reports an outcome consistent with that expectation, thereby confirming it.

参数：

- `expectation_reasoning: reasoning`：The reasoning stating the expected behavior, output, content, result, state, or constraint.
- `check_action: action`：The action executing an operation, inspection, or comparison capable of producing or observing the expected outcome.
- `result_observation: observation`：The observation reporting the outcome of the operation, inspection, or comparison.

成立条件：

- The reasoning states a specific behavior, output, content, result, state, or constraint that is expected to occur, be present, or be preserved.
- The action is directed at exercising, producing, observing, or comparing against that expectation.
- The observation reports content consistent with the stated expectation, without contradiction.

排除条件：

- No expected behavior, output, content, result, state, or constraint is identifiable in the reasoning.
- The action is unrelated to the expectation or only incidentally observes it.
- The observation contradicts the expectation or is inconclusive about it.
- The check confirms only bare existence or uninspected metadata without testing any stated expected result, content, state, or constraint.

### CLASSIFIES_FAILURE_AS_TEST_ARTIFACT

签名：`CLASSIFIES_FAILURE_AS_TEST_ARTIFACT(assessment_reasoning: reasoning, failure_observation: observation)`

The reasoning attributes an observed failure, anomaly, or misleading or empty result to the agent's own test setup, execution context, tooling, or measurement technique rather than to a defect in the target system being configured or built.

参数：

- `assessment_reasoning: reasoning`：The reasoning classifying the failure or anomalous result as induced by the agent's own testing, tooling, or measurement technique.
- `failure_observation: observation`：The observation reporting the failure, anomaly, or misleading or empty result.

成立条件：

- The observation reports a failure, error, anomaly, or empty or misleading result.
- The reasoning attributes that result to the agent's own test setup, execution context, tooling, or measurement technique.
- The reasoning distinguishes that cause from a genuine defect or limitation of the target system.

排除条件：

- The reasoning treats the failure as a genuine defect or limitation of the target system.
- The reasoning only restates the failure or identifies a cause without classifying it as induced by the agent's own setup or measurement method.
- The observation does not report a failure, anomaly, or misleading or empty result.

### SUCCESSFUL_CORRECTIVE_RETRY

签名：`SUCCESSFUL_CORRECTIVE_RETRY(failure_observation: observation, diagnosis_reasoning: reasoning, retry_action: action, retry_observation: observation)`

After an operation is observed to fail and its cause is diagnosed, a subsequent action revises that operation in a manner addressing the diagnosed cause, and the resulting observation shows the operation succeeding or the prior failure no longer occurring.

参数：

- `failure_observation: observation`：The observation reporting the initial failed or blocked operation.
- `diagnosis_reasoning: reasoning`：The reasoning identifying the cause of the failure and motivating the correction.
- `retry_action: action`：The revised action attempting the operation with a corrective change.
- `retry_observation: observation`：The observation reporting the result of the retry.

成立条件：

- The failure observation reports an unsuccessful or blocked operation.
- The diagnosis reasoning identifies a specific cause of that failure.
- The retry action differs from the failed operation in a manner that targets the diagnosed cause.
- The retry observation reports success or the absence of the prior failure.

排除条件：

- The retry repeats the original operation without addressing the diagnosed cause.
- No cause of the failure is diagnosed before the retry.
- The retry observation still shows the same failure or provides no outcome evidence.

### PLANS_MULTI_CRITERIA_VERIFICATION

签名：`PLANS_MULTI_CRITERIA_VERIFICATION(reasoning: reasoning)`

The reasoning enumerates a set of distinct conditions, artifacts, or behaviors to be confirmed before completion, forming a verification checklist whose items are observations or comparisons to be checked rather than modifications to be made.

参数：

- `reasoning: reasoning`：The agent text enumerating the conditions or criteria to be confirmed.

成立条件：

- The reasoning lists two or more distinct conditions, artifacts, or behaviors to be checked.
- The listed items are framed as things to confirm, inspect, or observe, not as actions that modify the system.
- At least one item includes an anticipated value, acceptance criterion, or expected state against which a later observation can be compared.

排除条件：

- The reasoning describes a single check without forming a multi-item verification set.
- The reasoning lists only modification steps with no confirmation criteria.
- The reasoning merely restates results already observed without enumerating conditions still to be confirmed.

### AUDITS_PLANNED_CRITERIA

签名：`AUDITS_PLANNED_CRITERIA(plan_reasoning: reasoning, audit_action: action, audit_result: observation)`

An action gathers current state for the specific conditions enumerated in a prior verification plan, and its result reports values or artifacts for those conditions so that each planned criterion can be checked against the returned state.

参数：

- `plan_reasoning: reasoning`：The reasoning enumerating the criteria to be verified.
- `audit_action: action`：The action that gathers the corresponding system state, possibly several checks in one invocation.
- `audit_result: observation`：The observation reporting the values or artifacts for the planned criteria.

成立条件：

- The plan_reasoning enumerates specific conditions to be confirmed.
- The audit_action inspects the aspects of the system that correspond to those conditions.
- The audit_result contains identifiable values for the planned criteria, sufficient to judge each one.

排除条件：

- The action probes aspects unrelated to the enumerated criteria.
- The observation does not report values for the planned criteria.
- No prior criteria were enumerated, so the action is exploratory rather than an audit of a plan.

### ASSESSES_ANOMALY_AS_NON_IMPACTING

签名：`ASSESSES_ANOMALY_AS_NON_IMPACTING(assessment_reasoning: reasoning, anomaly_observation: observation)`

The reasoning acknowledges that an anomaly reported in an observation is real but judges it inconsequential to the required functionality, grounding that judgment in independent evidence that the required function still succeeds.

参数：

- `assessment_reasoning: reasoning`：The agent text evaluating the significance of the observed anomaly.
- `anomaly_observation: observation`：The observation reporting the anomaly, such as an unexpected process state, leftover connection state, or stray artifact.

成立条件：

- The reasoning names the observed anomaly and states explicitly that it does not affect the required behavior.
- The judgment is supported by independent functional evidence, such as a successful operation exercising the same subsystem, rather than by assertion alone.

排除条件：

- The anomaly is dismissed without any explanation or supporting functional evidence.
- The reasoning treats the anomaly as a blocking problem that must be eliminated.
- The anomaly actually prevents or degrades the required functionality.

### DECODES_ENCODED_OBSERVATION

签名：`DECODES_ENCODED_OBSERVATION(interpretation_reasoning: reasoning, encoded_observation: observation)`

The reasoning translates low-level or encoded fields returned by an observation, such as numeric state codes, hexadecimal addresses, raw tables, or machine-oriented formats, into domain-level states, and the stated conclusion depends on that translation.

参数：

- `interpretation_reasoning: reasoning`：The agent text mapping raw fields to domain-level meanings.
- `encoded_observation: observation`：The observation whose content is in an encoded or machine-oriented form.

成立条件：

- The observation content is not stated in plain domain terms, such as codes, hexadecimal values, or raw tabular fields.
- The reasoning explicitly maps the encoded values to concrete domain states and derives its conclusion from that mapping.

排除条件：

- The observation already reports the state in plain semantic terms.
- The reasoning restates raw content without mapping it to domain meanings.
- The reasoning's conclusion does not depend on the decoded fields.

### REINVESTIGATES_SUSPECT_RESULT

签名：`REINVESTIGATES_SUSPECT_RESULT(doubt_reasoning: reasoning, recheck_action: action)`

The reasoning flags a check as inconclusive, empty, or suspicious, and the action re-examines the same underlying question using a different technique or source of evidence.

参数：

- `doubt_reasoning: reasoning`：The agent text expressing doubt about a prior or current result and the need to re-check.
- `recheck_action: action`：The action that re-examines the same question by alternative means.

成立条件：

- The reasoning expresses doubt, inconclusiveness, or suspicion about an existing result.
- The action addresses the same underlying question, using a different method, source, or tool than the earlier attempt.

排除条件：

- The action investigates a new question rather than the doubted result.
- No doubt or inconclusiveness about an existing result is expressed.
- The action simply repeats the identical probe that already produced the suspect result without changing technique.

### RESTORES_BASELINE_STATE

签名：`RESTORES_BASELINE_STATE(restore_action: action, restore_reasoning: reasoning)`

The action removes or reverts artifacts or state created during the agent's own operations so the target returns to a baseline condition, and the reasoning states that the purpose is to leave a clean starting point for subsequent use.

参数：

- `restore_action: action`：The action deleting or reverting artifacts or state produced by the agent's own operations.
- `restore_reasoning: reasoning`：The agent text stating the intent to return the target to its baseline or clean state.

成立条件：

- The action deletes, empties, or reverts state that was produced by the agent's own operations.
- The reasoning states that the goal is a clean or initial state for subsequent use without interference from the agent's operations.

排除条件：

- The action modifies state for a purpose other than reverting to the baseline condition.
- The reasoning only notes that cleanup finished without stating the baseline-state intent.
- The action removes artifacts but leaves the system in a state that still blocks the intended subsequent use.

### DETECTS_DATA_INCONSISTENCY

签名：`DETECTS_DATA_INCONSISTENCY(reasoning: reasoning)`

The reasoning identifies a concrete mismatch between an expected property of data, inferred from naming, metadata, specification, or labeling, and the property actually present in the observed data.

参数：

- `reasoning: reasoning`：The agent text pointing out the discrepancy between expectation and observed content.

成立条件：

- The reasoning explicitly contrasts an expected property of the data with the actually observed property.
- The discrepancy is concrete and identifiable, such as labels or identifiers not corresponding to the source indicated by the file or resource name.

排除条件：

- The reasoning merely summarizes or restates retrieved content without contrasting it against an expectation.
- The reasoning expresses generic uncertainty or surprise without identifying a specific mismatch.

### RESOLVES_AMBIGUITY_BY_INVARIANT_INTERPRETATION

签名：`RESOLVES_AMBIGUITY_BY_INVARIANT_INTERPRETATION(resolution_reasoning: reasoning, ambiguity_evidence: observation[])`

The reasoning resolves a detected ambiguity by adopting an interpretation or formulation whose outcome is identical under every plausible reading, so the ambiguity cannot affect the final result.

参数：

- `resolution_reasoning: reasoning`：The agent text evaluating interpretations and adopting the ambiguity-invariant one.
- `ambiguity_evidence: observation[]`：The observations whose content creates the ambiguity; support is collective.

成立条件：

- The reasoning enumerates at least two plausible interpretations of the ambiguous evidence.
- The reasoning argues that the same conclusion holds under each interpretation, or chooses the superset or union formulation that is safe under all of them.
- The reasoning explicitly adopts that invariant interpretation as the basis for subsequent work.

排除条件：

- The reasoning selects one interpretation arbitrarily or on stylistic grounds without showing outcome invariance.
- The chosen outcome would differ depending on which interpretation is correct.
- The ambiguity evidence is not referenced in the resolution reasoning.

### SEPARATES_MANDATORY_FROM_OPTIONAL_CRITERIA

签名：`SEPARATES_MANDATORY_FROM_OPTIONAL_CRITERIA(reasoning: reasoning)`

The reasoning classifies stated requirements into mandatory constraints and optional preferences, and assigns the preferences a subordinate role such as tie-breaking, so that only the mandatory constraints govern feasibility.

参数：

- `reasoning: reasoning`：The agent text performing the classification of requirements and assigning precedence.

成立条件：

- The reasoning explicitly marks at least one requirement as mandatory or hard and at least one other as a preference, soft, or informational.
- The reasoning states that preferences apply only when the mandatory constraints leave freedom, or that a preference cannot override a hard constraint.

排除条件：

- The reasoning treats all stated requirements uniformly, without distinguishing mandatory from optional.
- The reasoning only lists requirements without assigning them precedence.

### SELECTS_VALID_CANDIDATE_BY_ELIMINATION

签名：`SELECTS_VALID_CANDIDATE_BY_ELIMINATION(reasoning: reasoning)`

The reasoning systematically enumerates candidate options in a defined order and eliminates each candidate that violates any mandatory constraint, in order to select the first surviving candidate that satisfies all of them.

参数：

- `reasoning: reasoning`：The agent text enumerating candidates, eliminating violators, and naming the first surviving candidate.

成立条件：

- The reasoning considers multiple candidate options in a defined order.
- For each rejected candidate, the reasoning identifies at least one mandatory constraint that it violates.
- The reasoning names the first candidate that survives all constraints as the selected answer.

排除条件：

- The reasoning considers only a single candidate without comparison.
- Candidates are rejected without identifying which constraint they violate.
- The selection is made without any ordering or elimination procedure.

### VALIDATES_OUTPUT_BY_INDEPENDENT_CHECK

签名：`VALIDATES_OUTPUT_BY_INDEPENDENT_CHECK(claim_reasoning: reasoning, check_action: action, check_result: observation)`

An action executes a check procedure constructed independently of the original derivation to test an already-produced decision or output, and the resulting observation is interpreted as confirmation or refutation of that output.

参数：

- `claim_reasoning: reasoning`：The reasoning stating the decision or output to be validated and/or the intent to check it.
- `check_action: action`：The action executing the independent check procedure against the raw inputs and the produced output.
- `check_result: observation`：The observation reporting the check outcome from which pass or fail can be read.

成立条件：

- The reasoning states or references a decision or produced output that is to be validated.
- The check action applies a procedure that re-derives or re-tests the same requirements from raw inputs rather than merely displaying the output.
- The check result reports outcomes interpretable as passing or failing for that decision or output.

排除条件：

- The action merely re-displays the produced output without testing it against the requirements.
- The result cannot be interpreted as passing or failing the decision.
- No identifiable prior decision or output is being validated.

### VERIFIES_INPUT_INTEGRITY

签名：`VERIFIES_INPUT_INTEGRITY(inspection_action: action, inspection_observation: observation)`

The action inspects metadata, checksums, or other integrity-relevant state of input artifacts that must remain unmodified, and the resulting observation reports state from which the continued integrity (non-modification) of those inputs can be confirmed.

参数：

- `inspection_action: action`：The action inspecting timestamps, checksums, or directory listings of the protected input artifacts.
- `inspection_observation: observation`：The observation reporting the integrity-relevant state of those input artifacts.

成立条件：

- The action targets input artifacts whose preservation is required and inspects integrity-relevant state such as modification times, checksums, or existence.
- The observation reports that state in a form from which non-modification of the inputs can be judged.

排除条件：

- The action retrieves artifact content for use in computation rather than checking integrity.
- The observation does not report integrity-relevant state of the inputs.
- The action modifies the input artifacts instead of inspecting them.

### IDENTIFIES_PREREQUISITE_GAP

签名：`IDENTIFIES_PREREQUISITE_GAP(gap_reasoning: reasoning)`

The reasoning recognizes that a capability, dependency, resource, or input required to accomplish the task is absent, unavailable, or insufficient, thereby establishing a prerequisite gap that must be addressed before the task can proceed.

参数：

- `gap_reasoning: reasoning`：The agent text identifying a prerequisite needed for the task and characterizing it as missing or insufficient.

成立条件：

- The reasoning names or describes a capability, dependency, resource, or input that the task requires.
- The reasoning states or clearly implies that this prerequisite is currently absent, unavailable, or insufficient for the task.

排除条件：

- The reasoning only enumerates what is already available or installed without noting any deficiency.
- The reasoning identifies something as missing that is unrelated to accomplishing the stated task.
- The reasoning merely reports an error message without characterizing a required prerequisite as deficient.

### RESOLVES_AMBIGUITY_BY_COMMITTED_INTERPRETATION

签名：`RESOLVES_AMBIGUITY_BY_COMMITTED_INTERPRETATION(interpretation_reasoning: reasoning)`

The reasoning recognizes that a task specification, term, or requirement admits more than one plausible reading and commits to one specific reading as the basis for subsequent work, without requiring that the alternative readings yield the same outcome.

参数：

- `interpretation_reasoning: reasoning`：The agent text that identifies the ambiguity and selects the interpretation to be followed.

成立条件：

- The reasoning acknowledges uncertainty or multiple plausible readings of a requirement, term, or specification.
- The reasoning selects one specific reading and presents it as the interpretation that subsequent work will follow.

排除条件：

- The reasoning adopts a requirement or term without acknowledging any alternative reading.
- The reasoning merely restates the task wording without choosing among possible readings.
- The reasoning raises an ambiguity but leaves the interpretation unresolved for later work.

### MAPS_UNDERSPECIFIED_TERM_TO_CONCRETE_VALUES

签名：`MAPS_UNDERSPECIFIED_TERM_TO_CONCRETE_VALUES(mapping_reasoning: reasoning, documentation_observation: observation)`

The reasoning resolves a term in the task requirement or specification that does not literally match any value present in the target data, by using the content of reference material that enumerates or groups the corresponding concrete categories, sources, or aliases, and adopts those concrete values as the operative selection criterion.

参数：

- `mapping_reasoning: reasoning`：The reasoning that maps the underspecified requirement term onto concrete data values.
- `documentation_observation: observation`：The observation containing reference material content (documentation, schema, or specification) enumerating categories, sources, or aliases.

成立条件：

- The requirement or specification uses a term that does not literally match any value present in the data under consideration.
- The observation contains reference material content that enumerates or groups the concrete categories, sources, or aliases corresponding to that term.
- The reasoning uses that reference content to select the concrete values that correspond to the term and adopts them as the criterion for subsequent selection or filtering.

排除条件：

- The reasoning merely restates the requirement term without converting it into concrete values.
- The observation reports measurements or values of the target data rather than reference material enumerating categories.
- The reference content does not determine which concrete values correspond to the term.
- The mapping rests only on the agent's prior knowledge or guesswork without identifiable support from the observation.

### ENUMERATES_FAILURE_HYPOTHESES

签名：`ENUMERATES_FAILURE_HYPOTHESES(reasoning: reasoning)`

The reasoning presents two or more distinct candidate explanations for the same observed anomaly, missing state, or unexpected result, treating them as alternatives to be investigated or distinguished rather than committing to a single explanation.

参数：

- `reasoning: reasoning`：The agent text enumerating alternative explanations for the anomaly or missing state.

成立条件：

- The reasoning explicitly presents at least two distinct candidate causes or explanations for the same anomaly, missing state, or unexpected result.
- The candidates are framed as alternatives that must be investigated, distinguished, or otherwise resolved.

排除条件：

- The reasoning states only one diagnosis or conclusion.
- The reasoning merely reports the symptom or current state without proposing candidate causes.
- The reasoning lists optional actions rather than alternative explanations.
- The listed alternatives do not address the same anomaly or missing state.

### RECONSTRUCTS_EVENT_TIMELINE

签名：`RECONSTRUCTS_EVENT_TIMELINE(reasoning: reasoning)`

The reasoning reconstructs an ordered chronological sequence of past events from recorded history and uses that ordering to explain how the current state or artifact configuration arose.

参数：

- `reasoning: reasoning`：The agent text reconstructing the historical sequence and its relation to the current state.

成立条件：

- The reasoning orders at least two recorded events in time.
- The reasoning explicitly relates the sequence of past events to the current system, artifact, data, or repository state.
- The reconstruction provides temporal or causal connections among the events.

排除条件：

- The reasoning lists historical entries without ordering or interpreting them.
- The reasoning discusses only a single past event.
- The reasoning reports only the current state without reconstructing how it arose.

### DIAGNOSES_LOST_STATE_CAUSE

签名：`DIAGNOSES_LOST_STATE_CAUSE(reasoning: reasoning)`

The reasoning concludes a specific causal explanation for why expected content, an artifact, or a state is absent from the current view, identifying the operation or sequence that detached, discarded, hid, overwrote, or otherwise removed it.

参数：

- `reasoning: reasoning`：The agent text stating the causal explanation for the missing content, artifact, or state.

成立条件：

- The reasoning states a cause for content, an artifact, or a state being absent from the current view.
- The reasoning identifies the operation or sequence of operations responsible for the loss, detachment, hiding, or overwriting.
- The explanation is presented as a conclusion rather than only as an unexamined possibility.

排除条件：

- The reasoning only enumerates possible causes without selecting or supporting one.
- The reasoning only reports the current location or absence of the missing content.
- The reasoning identifies where an artifact is but provides no causal explanation for its absence.

### CONSULTS_HISTORY_TO_LOCATE_LOST_ARTIFACT

签名：`CONSULTS_HISTORY_TO_LOCATE_LOST_ARTIFACT(action: action, observation: observation)`

An action queries historical records, reflogs, audit trails, backups, or unreachable-object stores to locate an artifact or state absent from the current visible state, and the observation returns historical entries or orphaned objects identifying the missing artifact.

参数：

- `action: action`：The action querying historical records, reflogs, audit trails, backups, or unreachable-object stores.
- `observation: observation`：The result returning historical entries or orphaned artifacts not visible in the current state.

成立条件：

- The action targets historical records or a recovery store rather than only the current working state.
- The observation returns prior-state entries, orphaned objects, or historical references that are not present in the current visible state.
- The returned information can be used to locate the missing artifact or state.

排除条件：

- The action inspects only current files, current references, or current status.
- The observation contains no historical or unreachable-artifact information.
- The historical query is unrelated to locating a missing artifact or state.

### DISAMBIGUATES_CANDIDATES_BY_PROVENANCE

签名：`DISAMBIGUATES_CANDIDATES_BY_PROVENANCE(reasoning: reasoning, observation: observation)`

The reasoning selects one among multiple candidate artifacts as the intended target by comparing provenance attributes reported in an observation, such as authorship, timing, origin, or parentage, and rejects or sets aside at least one alternative.

参数：

- `reasoning: reasoning`：The agent text comparing candidates and selecting the intended target.
- `observation: observation`：The observation reporting provenance attributes for the candidate artifacts.

成立条件：

- The observation reports distinguishable provenance attributes for at least two candidate artifacts.
- The reasoning uses at least one provenance attribute to select one candidate as the intended target.
- The reasoning explicitly or implicitly rejects or sets aside at least one other candidate on the basis of the reported provenance.

排除条件：

- Only one candidate artifact is considered.
- The selection is based solely on content similarity or arbitrary preference without provenance evidence.
- The observation lacks attributes that distinguish the candidates.

### PREDICTS_CONFLICT_FROM_OVERLAPPING_CHANGES

签名：`PREDICTS_CONFLICT_FROM_OVERLAPPING_CHANGES(reasoning: reasoning, observation: observation)`

The reasoning predicts, before attempting integration, that combining two versions will produce a conflict because an observation shows that both versions changed the same artifact or overlapping regions.

参数：

- `reasoning: reasoning`：The agent text predicting that integration will conflict in a particular artifact or region.
- `observation: observation`：The observation showing changes from both versions in the same artifact or overlapping regions.

成立条件：

- The observation identifies changes from both sides to the same artifact or overlapping regions.
- The reasoning predicts that combining or merging the versions will conflict in that artifact or region before the operation is attempted.
- The predicted conflict is explicitly tied to the observed overlap.

排除条件：

- Only one side is observed to have changed the artifact or region.
- The reasoning predicts conflict without evidence of overlapping changes.
- The conflict is discovered only after an integration operation is attempted rather than predicted from comparison.

### JUSTIFIES_CONFLICT_RESOLUTION_PRECEDENCE

签名：`JUSTIFIES_CONFLICT_RESOLUTION_PRECEDENCE(reasoning: reasoning)`

The reasoning chooses which side of an identified conflict should prevail and justifies that choice by a substantive criterion such as recency, authority, intended semantics, precedence, or supersession.

参数：

- `reasoning: reasoning`：The agent text choosing and justifying the side of the conflict to retain.

成立条件：

- The reasoning identifies conflicting versions or changes.
- The reasoning selects one side to prevail.
- The reasoning provides a substantive criterion explaining why the selected side supersedes the other.

排除条件：

- The reasoning describes both sides without choosing one.
- The reasoning selects a side without giving any substantive justification.
- No conflict is identified in the reasoning.

### VERIFIES_EXACT_REPRESENTATION_BEFORE_TRANSFORMATION

签名：`VERIFIES_EXACT_REPRESENTATION_BEFORE_TRANSFORMATION(action: action, observation: observation)`

An action retrieves the exact byte-level or formatting-level representation of source content that is about to be reproduced, transformed, or adopted, and the observation reports those exact details so that the subsequent operation can preserve fidelity.

参数：

- `action: action`：The action retrieving byte-level or formatting-level details of the source content.
- `observation: observation`：The result reporting exact bytes, encoding, line endings, trailing whitespace, or content length.

成立条件：

- The action queries an exact representation of content intended for reproduction, transformation, or adoption.
- The observation reports byte-level or formatting-level details rather than only semantic content.
- The check occurs before the source content is written, merged, transformed, or otherwise reproduced.

排除条件：

- The action reads only semantic content without exact-format details.
- The exact-content check occurs after the content has already been written, merged, transformed, or otherwise reproduced.
- The observation does not report details relevant to preserving content fidelity.

### ELIMINATES_HYPOTHESIS_WITH_NEGATIVE_EVIDENCE

签名：`ELIMINATES_HYPOTHESIS_WITH_NEGATIVE_EVIDENCE(reasoning: reasoning, observation: observation)`

The reasoning rules out or deprioritizes a candidate explanation because an observation reports that an expected trace, condition, or indicator required by that explanation is absent.

参数：

- `reasoning: reasoning`：The agent text using the absence of an expected indicator to rule out or deprioritize a candidate explanation.
- `observation: observation`：The observation reporting a clean state or the absence of an expected trace or condition.

成立条件：

- The reasoning names a candidate explanation that would require a particular trace or condition to be present.
- The observation reports that the required trace or condition is absent.
- The reasoning concludes that the candidate explanation is unlikely or eliminated because of that absence.

排除条件：

- The observation confirms the presence of the expected trace rather than its absence.
- The absence is merely noted without being used to eliminate or deprioritize a hypothesis.
- The absent evidence is unrelated to the candidate explanation.

### INTERPRETS_CONFLICT_MARKERS_AS_COMPETING_VERSIONS

签名：`INTERPRETS_CONFLICT_MARKERS_AS_COMPETING_VERSIONS(interpretation_reasoning: reasoning, conflict_observation: observation)`

The reasoning interprets an observation that displays explicit divergence markers or clearly divergent alternative renderings of the same artifact as a conflict between competing versions, and identifies at least one side or the scope of that divergence.

参数：

- `interpretation_reasoning: reasoning`：The reasoning that recognizes the alternatives as competing versions and characterizes the conflict.
- `conflict_observation: observation`：The observation displaying divergence markers or divergent alternative content for the same artifact.

成立条件：

- The observation contains explicit divergence markers, such as conflict markers, or clearly divergent alternative versions of the same artifact.
- The reasoning identifies the situation as a conflict or divergence between competing versions.
- The reasoning identifies at least one side or the scope of the conflicting content.

排除条件：

- The observation contains no divergence markers and no divergent alternative versions.
- The reasoning merely repeats the observation without recognizing a conflict or divergence.
- The reasoning discusses a conflict that is not evidenced by the observation.

### ADOPTS_OBSERVED_EXACT_REPRESENTATION_AS_CONSTRAINT

签名：`ADOPTS_OBSERVED_EXACT_REPRESENTATION_AS_CONSTRAINT(spec_reasoning: reasoning, exact_representation_observation: observation)`

The reasoning takes precise byte- or character-level representation details reported by an observation, such as byte count, trailing whitespace, or final-newline status, and treats them as binding constraints for reproducing, transforming, or adopting the artifact.

参数：

- `spec_reasoning: reasoning`：The reasoning that restates observed exact details and adopts them as constraints.
- `exact_representation_observation: observation`：The observation reporting exact byte- or character-level details of the artifact.

成立条件：

- The observation reports exact representation details of an artifact intended for reproduction, transformation, or adoption, such as byte count, whitespace, or newline status.
- The reasoning explicitly restates those details.
- The reasoning uses the restated details as constraints that govern a subsequent reproduction, transformation, or adoption action or method.

排除条件：

- The reasoning cites only general semantic content from the observation.
- The reasoning notes the details without making them constrain any subsequent reproduction, transformation, or adoption.
- The observation lacks exact representation details.

### RESOLVES_CONFLICT_BY_ADOPTING_DESIGNATED_VERSION

签名：`RESOLVES_CONFLICT_BY_ADOPTING_DESIGNATED_VERSION(resolution_decision_reasoning: reasoning, resolution_action: action, completion_observation: observation)`

The reasoning designates one competing version as the side to adopt in an identified conflict, the action applies that version and completes the finalization step, and the observation confirms successful finalization with no unresolved conflict state.

参数：

- `resolution_decision_reasoning: reasoning`：The reasoning designating a conflict side and intending to finalize the resolution.
- `resolution_action: action`：The action adopting the designated version and finalizing the conflict resolution, for example by staging and committing or otherwise completing it.
- `completion_observation: observation`：The observation confirming that the resolution was finalized successfully and no conflict state remains.

成立条件：

- The reasoning identifies a side or version to adopt in a conflict and intends to finalize the resolution.
- The action adopts that designated side and performs the finalization step, such as staging and committing or otherwise completing the resolution.
- The observation confirms that the resolution completed successfully, for example by reporting a new result commit and a clean working state.

排除条件：

- The action only inspects or displays the conflict without resolving it.
- No side or version is designated for adoption.
- The observation does not confirm finalization, or the conflict remains unresolved.

### SUMMARIZES_COMPLETED_TASK_WITH_VERIFIED_OUTCOME

签名：`SUMMARIZES_COMPLETED_TASK_WITH_VERIFIED_OUTCOME(completion_summary_reasoning: reasoning)`

The reasoning provides a final synthesis that explains the original problem or its cause, the remediation actions taken, and the resulting state established by verified evidence, and presents the task as complete.

参数：

- `completion_summary_reasoning: reasoning`：The reasoning providing the final task synthesis and conclusion.

成立条件：

- The reasoning presents a final answer or explicitly concludes that the task is complete.
- The reasoning summarizes the original problem or cause and the actions taken to address it.
- The reasoning cites a verified resulting state or evidence of the outcome.

排除条件：

- The reasoning is an intermediate plan, status update, or progress note.
- The reasoning does not synthesize cause, actions, and outcome.
- The reasoning claims completion without any verified outcome evidence.

### FRAMES_OBJECTIVE_WITH_CONSTRAINTS

签名：`FRAMES_OBJECTIVE_WITH_CONSTRAINTS(reasoning: reasoning)`

The reasoning explicitly states a target objective to be achieved together with one or more constraints, prohibitions, or preservation requirements that limit acceptable actions or outcomes.

参数：

- `reasoning: reasoning`：The agent text framing the objective and its associated constraints.

成立条件：

- The reasoning states a goal or desired outcome to be achieved.
- The reasoning states at least one constraint, prohibition, or preservation requirement relevant to that goal.

排除条件：

- The reasoning only lists planned actions without stating any constraint or preservation requirement.
- The reasoning only reports completed outcomes without framing an objective and its constraints.
- The reasoning states a constraint without identifying any objective or goal.

### EXPLAINS_ANOMALOUS_OBSERVATION_WITH_CAUSAL_MECHANISM

签名：`EXPLAINS_ANOMALOUS_OBSERVATION_WITH_CAUSAL_MECHANISM(reasoning: reasoning, observation: observation)`

The reasoning explains an observation that is unexpected, apparently inconsistent with prior expectations, or notably absent by identifying a causal mechanism that accounts for it.

参数：

- `reasoning: reasoning`：The reasoning that explains the apparent anomaly using a causal mechanism.
- `observation: observation`：The observation reporting the unexpected, absent, or apparently inconsistent result.

成立条件：

- The observation reports a result that is unexpected, apparently inconsistent with prior evidence or expectations, or notably absent.
- The reasoning identifies a causal mechanism that resolves or accounts for the apparent anomaly.
- The explanation is presented as an inference about why the observation occurred or did not occur.

排除条件：

- The observation is consistent with expectations and no anomaly is addressed.
- The reasoning merely restates the observation or draws an ordinary conclusion without explaining an anomaly.
- The reasoning only notes surprise or inconsistency without identifying a causal mechanism.

### IS_VERIFICATION_ACTION

签名：`IS_VERIFICATION_ACTION(action: action)`

The action is directed at checking whether an outcome, postcondition, or constraint holds, rather than at making the primary change.

参数：

- `action: action`：The action being assessed as a verification action.

成立条件：

- The action performs an inspection, comparison, search, or read whose purpose is to confirm a state or result.
- The action is not primarily a creation, modification, deletion, or initial discovery operation.
- The check is directed at a result, postcondition, or constraint that is already relevant to the task.

排除条件：

- The action's primary purpose is to create, modify, or remove data.
- The action is exploratory discovery with no prior result or constraint being checked.
- The action performs a check but the check is incidental to a primary modification.

### CONFIRMS_TARGET_ABSENCE_ACROSS_SEARCH_SPACE

签名：`CONFIRMS_TARGET_ABSENCE_ACROSS_SEARCH_SPACE(verification_action: action, verification_result: observation, requirement_reasoning: reasoning)`

A verification action searches multiple relevant locations or representations of a target domain, and its observation reports that a specified target is absent from all searched locations, confirming its removal or non-presence relative to a requirement.

参数：

- `verification_action: action`：The action that searches multiple relevant locations or representations for the target.
- `verification_result: observation`：The observation reporting whether the target was found in the searched locations.
- `requirement_reasoning: reasoning`：The reasoning establishing that the target must not remain in the searched space.

成立条件：

- The requirement reasoning establishes that a specified target must not remain in the searched space.
- The verification action searches multiple relevant locations or representations for that target.
- The verification result reports no occurrence of the target in those locations.

排除条件：

- The action finds the target or does not report absence.
- The search covers only a single superficial location or does not target the specified item.
- No requirement of absence is identified.

### VALIDATES_NON_INTERFERENCE_WITH_PROTECTED_CONTENT

签名：`VALIDATES_NON_INTERFERENCE_WITH_PROTECTED_CONTENT(verification_action: action, verification_result: observation, constraint_reasoning: reasoning)`

A verification action inspects content or metadata that a preservation constraint requires to remain unchanged, and its observation indicates that the protected content is intact, supporting a non-interference constraint.

参数：

- `verification_action: action`：The action inspecting protected content or its metadata after an intervention.
- `verification_result: observation`：The observation indicating whether the protected content remains intact.
- `constraint_reasoning: reasoning`：The reasoning stating that specified unrelated content, files, messages, or history must remain unchanged.

成立条件：

- The constraint reasoning states that specified unrelated content, files, messages, or history must remain unchanged.
- The verification action inspects those protected items or their state after an intervention.
- The verification result indicates the inspected items remain present and unchanged or consistent with their prior state.

排除条件：

- The action only checks removal or correctness of the target and does not inspect protected unrelated content.
- The observation does not provide evidence about preservation of unrelated content.
- No preservation constraint is identified.

### SELECTS_CAUSE_DIRECTED_REMEDIATION

签名：`SELECTS_CAUSE_DIRECTED_REMEDIATION(reasoning: reasoning)`

The reasoning identifies an underlying mechanism that causes a target to persist or remain detectable, and selects or proposes a remediation directed at eliminating that mechanism rather than only removing a visible instance.

参数：

- `reasoning: reasoning`：The reasoning identifying the persistence mechanism and selecting a remediation for it.

成立条件：

- The reasoning identifies a specific persistence or retention mechanism.
- The reasoning selects or proposes an intervention that acts on that identified mechanism.

排除条件：

- The reasoning proposes generic cleanup without linking it to an identified persistence mechanism.
- The reasoning only reports that remediation was performed.
- The reasoning identifies a symptom but not a persistence or retention mechanism.

### ENACTS_DERIVED_CONSTRAINT

签名：`ENACTS_DERIVED_CONSTRAINT(constraint_reasoning: reasoning, action: action)`

The reasoning derives a necessary condition that must hold for the target system to function as required, and the action performs an operation that establishes that condition.

参数：

- `constraint_reasoning: reasoning`：The reasoning stating a necessary condition or implication required for the system to work correctly, derived from requirements or observed runtime facts.
- `action: action`：The recorded invocation that brings about the stated necessary condition.

成立条件：

- The reasoning states a necessary condition or implication that must hold for the target system to work correctly, derived from task requirements or observed runtime facts rather than merely asserted as a goal.
- The action performs an operation that establishes that condition, for example by adjusting ownership, permissions, or other required settings.

排除条件：

- The reasoning states only a general goal or desired outcome without a derived necessary condition.
- The action satisfies some requirement that the reasoning never expressed as a condition.
- The reasoning states the condition but no corresponding action establishes it.

### VERIFIES_CHANGE_EFFECT

签名：`VERIFIES_CHANGE_EFFECT(change_action: action, verification_observation: observation)`

An action applies or initiates a state change on a targeted object, and the observation reports the resulting state of that same object in a form that shows whether the intended effect of the change is present.

参数：

- `change_action: action`：The recorded invocation that applies or initiates the state change.
- `verification_observation: observation`：The observation reporting the post-change state of the targeted object.

成立条件：

- The action performs or initiates a state change on a targeted object, such as starting a service, writing a file, creating a resource, or altering configuration.
- The observation reports the resulting state of that same targeted object in a form from which the presence or absence of the intended effect can be read.

排除条件：

- The observation reports only pre-change state or output unrelated to the changed object.
- The action is a pure read that changes nothing.
- The observation reports that the intended effect of the change is absent.

### REMOVES_SUPERSEDED_ARTIFACTS_TO_RESOLVE_CONFLICT

签名：`REMOVES_SUPERSEDED_ARTIFACTS_TO_RESOLVE_CONFLICT(cleanup_action: action, conflict_reasoning: reasoning)`

The reasoning identifies a duplication or conflict in which redundant artifacts overlap or compete with an authoritative configuration that is to be preserved, and the action removes those redundant artifacts so that only the authoritative configuration remains in effect.

参数：

- `cleanup_action: action`：The action that deletes or disables the redundant or conflicting artifacts.
- `conflict_reasoning: reasoning`：The reasoning that identifies the duplication or conflict, designates the authoritative configuration to keep, and prescribes removal of the redundant artifacts.

成立条件：

- The reasoning identifies a duplication or conflict between redundant artifacts (typically those the agent itself created) and an authoritative configuration or artifact that should be preserved.
- The cleanup action removes or disables those specific redundant or conflicting artifacts.
- The authoritative configuration referenced in the reasoning is left in place and remains the operative one after the action.

排除条件：

- The action removes artifacts without any identified duplication or conflict, such as routine tidying of unrelated files.
- The action merely overwrites, patches, or reconfigures the offending artifact instead of removing or disabling it.
- The reasoning identifies the conflict but no corresponding removal action is performed.
- The removed artifacts are neither the agent's own redundant artifacts nor duplicates of a configuration that is being preserved.

### PLANS_WITH_FALLBACK

签名：`PLANS_WITH_FALLBACK(reasoning: reasoning)`

The reasoning states a primary course of action together with an explicit contingent alternative that will be used if the primary approach is unavailable, fails, or an expected enabling condition is not met, so both courses remain available rather than one being discarded.

参数：

- `reasoning: reasoning`：The agent text presenting the primary course of action and the contingent alternative held in reserve.

成立条件：

- The reasoning identifies a primary action or approach that the agent intends to attempt.
- The reasoning identifies at least one alternative action or approach explicitly conditioned on the primary approach failing, being unavailable, or its enabling condition not holding.
- Both the primary and the contingent alternative are retained as viable courses of action.

排除条件：

- The reasoning presents only a single course of action or an unconditional sequence of steps.
- The reasoning mentions alternatives without tying them to a contingency that triggers them.
- The reasoning weighs mutually exclusive candidates and selects one while abandoning the others, which is option selection rather than fallback planning.

### ANALYZES_EXTERNAL_VALIDATION_RISK

签名：`ANALYZES_EXTERNAL_VALIDATION_RISK(reasoning: reasoning)`

The reasoning models plausible procedures, assumptions, or edge cases of an external validator, test harness, or consumer of the deliverable, and identifies a specific condition under which the current or planned system state would fail that validation.

参数：

- `reasoning: reasoning`：The agent text reasoning about how an external validator might behave and where the current or planned state could fail it.

成立条件：

- The reasoning describes at least one plausible procedure, command sequence, assumption, or edge case that an external validator or consumer of the deliverable might exhibit.
- The reasoning identifies a concrete condition under which the current or planned system state would fail under that validation.
- The identified risk concerns externally imposed validation rather than the agent's own planned checks.

排除条件：

- The reasoning only plans the agent's own verification steps.
- The reasoning expresses generic concern or uncertainty without naming a validator behavior and a corresponding failure condition.
- No external validation or downstream consumer of the deliverable is under consideration.
- The reasoning only explains a failure that has already been observed rather than anticipating a possible validation outcome.

### SELECTS_UNDERTESTED_PATH_FOR_VERIFICATION

签名：`SELECTS_UNDERTESTED_PATH_FOR_VERIFICATION(selection_reasoning: reasoning)`

The reasoning identifies a specific behavior, path, or condition that prior verification did not exercise and proposes an additional check for it, explaining what that check would reveal about the implementation or requirements.

参数：

- `selection_reasoning: reasoning`：The reasoning identifying an unexercised behavior, path, or condition and proposing a check for it.

成立条件：

- The reasoning identifies a specific behavior, path, or condition that earlier verification did not exercise.
- The reasoning proposes an additional check directed at that unexercised behavior, path, or condition.
- The reasoning states what the proposed check would reveal or confirm about the implementation or requirements, such as whether update or replacement logic behaves differently from initial creation.
- The proposed check is treated as pending at the time of the reasoning rather than already performed and confirmed.

排除条件：

- The reasoning proposes repeating a check that was already performed and confirmed.
- The reasoning lists planned steps without identifying any specific untested behavior, path, or condition.
- The proposed work concerns cleanup, reporting, or modification rather than verification of behavior.
- No specific unexercised behavior, path, or condition is identified.

### MEASURES_OPERATION_LATENCY

签名：`MEASURES_OPERATION_LATENCY(timed_action: action)`

The action instruments a specific operation with timing markers and computes or reports the elapsed duration attributable to that operation, producing a quantified latency measurement.

参数：

- `timed_action: action`：The action that brackets a specific operation with timing markers and computes or reports its elapsed duration.

成立条件：

- The action records a time marker before and after a specific operation.
- The action computes or reports the elapsed duration attributable to that operation from those markers.
- The measured operation is identifiable as the interval between the timing markers.

排除条件：

- The action reports a timestamp or duration without bracketing any specific operation.
- The timing markers span multiple unrelated operations so the resulting value cannot be attributed to one operation.
- The action does not compute or report an elapsed duration.

### EVALUATES_RESULT_AGAINST_ACCEPTANCE_CRITERION

签名：`EVALUATES_RESULT_AGAINST_ACCEPTANCE_CRITERION(evaluation_reasoning: reasoning, measured_observation: observation)`

The reasoning compares a concrete value, measurement, property, or outcome reported in the observation against a stated requirement, threshold, or expected property and judges whether that criterion is satisfied.

参数：

- `evaluation_reasoning: reasoning`：The reasoning that states the requirement, threshold, or expected property and renders a compliance judgment.
- `measured_observation: observation`：The observation supplying the concrete value, measurement, property, or outcome being judged.

成立条件：

- The observation contains an identifiable concrete value, measurement, property, or outcome.
- The reasoning states a requirement, threshold, or expected property and explicitly relates the observed value, measurement, property, or outcome to it.
- The reasoning concludes that the criterion is met or not met.

排除条件：

- The reasoning cites the observed result without comparing it to any stated requirement, threshold, or expected property.
- The comparison is asserted without an observed value or property to compare.
- The observation lacks the value, measurement, property, or outcome that the requirement concerns.
- The reasoning only restates the observation without rendering a compliance judgment.

### DECLARES_TASK_COMPLETION_WITH_REQUIREMENT_MAPPING

签名：`DECLARES_TASK_COMPLETION_WITH_REQUIREMENT_MAPPING(completion_reasoning: reasoning)`

The reasoning explicitly claims that the overall task is complete and itemizes multiple stated requirements alongside the outcomes or evidence that satisfy them, forming a final accountability record rather than an interim status update.

参数：

- `completion_reasoning: reasoning`：The reasoning containing the completion claim and the requirement-to-outcome or requirement-to-evidence mapping.

成立条件：

- The reasoning explicitly claims that the overall task is complete.
- The reasoning enumerates multiple requirements taken from the task statement or specification.
- Each enumerated requirement is associated with a satisfied outcome or identifiable evidence.
- No requirement is presented as satisfied while also being described as unresolved.

排除条件：

- The reasoning is an interim status report without a completion claim.
- The reasoning asserts completion without mapping requirements to outcomes or evidence.
- The reasoning lists some requirements as unresolved while still claiming full completion.
- The reasoning maps only a single requirement rather than multiple stated requirements.

### INTERPRETS_SPECIFICATION_CONSTRAINT

签名：`INTERPRETS_SPECIFICATION_CONSTRAINT(reasoning: reasoning)`

The reasoning interprets a stated requirement, schema, contract, or acceptance condition and derives a concrete implementation, validation, or response decision from it, including committing to how an ambiguous requirement should be applied.

参数：

- `reasoning: reasoning`：The agent text interpreting a stated requirement or acceptance condition and deriving a concrete implementation or validation decision from it.

成立条件：

- The reasoning explicitly references a stated requirement, schema, contract, or acceptance condition.
- The reasoning derives a concrete implementation, validation, response, or formatting decision from that requirement rather than merely restating it.

排除条件：

- The reasoning only restates or paraphrases a requirement without deriving any implementation or validation decision.
- The reasoning makes an implementation choice without connecting it to a stated requirement or acceptance condition.
- The reasoning evaluates observed results against a requirement instead of deciding how the requirement should be implemented or enforced.

### SELECTS_ALTERNATIVE_TOOL_AFTER_UNAVAILABILITY

签名：`SELECTS_ALTERNATIVE_TOOL_AFTER_UNAVAILABILITY(unavailability_observation: observation, adaptation_reasoning: reasoning, alternative_action: action)`

An observation reports that an intended tool, command, capability, or method is unavailable or unusable, and the reasoning selects a functionally equivalent alternative approach that a subsequent action then invokes in pursuit of the same objective.

参数：

- `unavailability_observation: observation`：The observation reporting that the intended tool, command, capability, or method is missing, not found, or otherwise unavailable.
- `adaptation_reasoning: reasoning`：The reasoning selecting a functionally equivalent alternative tool or method for the same objective.
- `alternative_action: action`：The invocation that uses the selected alternative tool or method.

成立条件：

- The observation reports that an intended tool, command, capability, or method is missing, not found, or otherwise unavailable.
- The reasoning explicitly selects a different tool, command, or method intended to accomplish the same objective.
- The alternative action invokes that selected alternative rather than repeating the unavailable one.

排除条件：

- The observed failure is unrelated to tool or method availability, such as an incorrect argument, a defect in the produced artifact, or a rejected input.
- The reasoning only acknowledges the unavailability without selecting an alternative.
- The alternative action is unrelated to the unavailable tool or does not serve the same objective.
- The selection contrasts candidate approaches before any unavailability is observed, without a specific unusable tool motivating the switch.

### ASSESSES_PERSISTENCE_BY_DEPLOYMENT_MECHANISM

签名：`ASSESSES_PERSISTENCE_BY_DEPLOYMENT_MECHANISM(persistence_reasoning: reasoning)`

The reasoning evaluates whether a launched process or started service will survive beyond the current session or command context, justifying that assessment from properties of the deployment mechanism (such as detachment, signal handling, or output redirection) rather than from the mere fact that the process is currently executing.

参数：

- `persistence_reasoning: reasoning`：The reasoning that raises the post-session survival question for a launched process or service and justifies its answer from deployment mechanics.

成立条件：

- The reasoning identifies a persistence or lifecycle concern for a launched process or started service, such as whether it survives session termination.
- The reasoning explains why the process should or should not survive by appealing to a deployment mechanism, such as detachment, ignore-signal handling, backgrounding, or output redirection.
- The persistence conclusion is derived from that mechanism rather than from merely observing that the process is currently running.

排除条件：

- The reasoning only states that the process is currently running or reachable.
- No durability or post-session survival question is considered.
- The reasoning asserts persistence without any mechanism-based justification.
- The reasoning merely plans to guard against a failure mode without assessing whether the deployed process will persist.

### REPORTS_EXECUTION_ERROR

签名：`REPORTS_EXECUTION_ERROR(observation: observation)`

The observation reports that an attempted operation did not succeed, conveying an error status, failure message, missing-tool or missing-resource fault, or rejected-request indication rather than a valid result of the requested operation.

参数：

- `observation: observation`：The observation conveying non-success of the attempted operation.

成立条件：

- The observation carries an identifiable non-success indication, such as an explicit error flag, an error or failure message, a missing command or resource fault, or a rejected request.
- The indication concerns the operation that was attempted, so that the attempt is not confirmed as successful.

排除条件：

- The observation reports successful completion or a normal result value of the requested operation.
- The observation reports a negative fact about the domain state, such as an empty directory, an absent key, or a missing artifact, while the operation itself succeeded.
- The observation reports an outcome of a diagnostic check whose result is a valid, usable answer to the question posed.

### JUDGES_PRIOR_RESULT_INCONCLUSIVE

签名：`JUDGES_PRIOR_RESULT_INCONCLUSIVE(reasoning: reasoning, observation: observation)`

The reasoning assesses a prior observation as insufficient, ambiguous, or otherwise uninformative for establishing the targeted state, because its reported content is empty, errored, or cannot discriminate between the possible answers to the question posed.

参数：

- `reasoning: reasoning`：The reasoning that evaluates the prior observation as inconclusive for the targeted state.
- `observation: observation`：The prior observation whose result is judged insufficient, ambiguous, or uninformative.

成立条件：

- The reasoning refers to an earlier observation and characterizes its content as empty, ambiguous, failed, or otherwise unable to establish the targeted state.
- The reasoning explains why that result does not settle the question, for example by noting that the content cannot distinguish between the possible conditions or that a further, different check is required.

排除条件：

- The reasoning treats the prior observation as definitive confirmation or disconfirmation of the targeted state.
- The reasoning does not refer to any prior observation.
- The observation is unrelated to the state the reasoning is trying to establish.

### DISAMBIGUATES_FALSE_POSITIVE_MATCH

签名：`DISAMBIGUATES_FALSE_POSITIVE_MATCH(reasoning: reasoning, observation: observation)`

The reasoning explains that an apparent match or candidate present in an observation does not satisfy the sought condition because the matching content originates from incidental, contextual, or unrelated material, and thereby distinguishes it from a genuine match.

参数：

- `reasoning: reasoning`：The reasoning that explains why the apparent match is a false positive.
- `observation: observation`：The observation containing the apparent match or candidate.

成立条件：

- The observation contains at least one apparent candidate match for a sought condition or target.
- The reasoning explains why that candidate does not actually satisfy the condition, citing the incidental, contextual, or unrelated origin of the matching content.
- The reasoning distinguishes the false positive from a genuine match, or concludes that no genuine match exists among the apparent candidates.

排除条件：

- The reasoning accepts the apparent match as genuine without explanation.
- The reasoning does not identify any apparent match in the observation.
- The reasoning merely states that no match is present without explaining why a candidate was misleading.
- The reasoning dismisses the candidate without explaining where the matching content came from.

### CHECKS_REQUIREMENTS_AGAINST_OBSERVED_STATE

签名：`CHECKS_REQUIREMENTS_AGAINST_OBSERVED_STATE(requirement_reasoning: reasoning, evidence_observations: observation[])`

The reasoning enumerates multiple distinct requirements, deliverables, or acceptance conditions and treats facts drawn collectively from observations as evidence of whether each enumerated item is satisfied.

参数：

- `requirement_reasoning: reasoning`：The reasoning that enumerates requirements or deliverables and assesses them against observed facts.
- `evidence_observations: observation[]`：The observations that collectively supply facts corresponding to the enumerated requirements; support is collective.

成立条件：

- The reasoning identifies or enumerates multiple distinct requirements, deliverables, or acceptance conditions.
- The evidence observations collectively report facts that correspond to those enumerated requirements.
- The reasoning maps or assesses those observed facts against the requirements rather than merely restating the task statement.

排除条件：

- The reasoning lists requirements without relating them to observed facts.
- The observations do not contain facts that address the enumerated requirements.
- Only a single requirement is assessed, so no multi-requirement evidence mapping is present.
- The reasoning restates the task requirements without any observed evidence for their satisfaction.

### REVISES_BELIEF_WITH_NEW_EVIDENCE

签名：`REVISES_BELIEF_WITH_NEW_EVIDENCE(revision_reasoning: reasoning, evidence_observation: observation)`

The reasoning explicitly corrects or updates an earlier belief, interpretation, or hypothesis in response to identifiable new evidence reported by an observation, and states the revised belief.

参数：

- `revision_reasoning: reasoning`：The reasoning text that supersedes a prior belief and states the revised belief or interpretation.
- `evidence_observation: observation`：The observation supplying the new evidence that motivates the revision.

成立条件：

- The reasoning refers to a prior belief, hypothesis, or provisional interpretation and presents it as superseded or corrected.
- The reasoning changes or corrects that belief in response to identifiable content of the observation.
- The reasoning states what the revised belief is.

排除条件：

- The reasoning merely repeats the observation without referencing a prior belief.
- The observation is unrelated to the belief being revised.
- No prior belief or provisional interpretation is identifiable in the reasoning.
- The reasoning only revises a planned course of action rather than a belief, hypothesis, or interpretation.

### IDENTIFIES_DATA_AMBIGUITY

签名：`IDENTIFIES_DATA_AMBIGUITY(reasoning: reasoning)`

The reasoning recognizes that a token, field value, or record in the data being processed can occupy more than one semantic role or context, creating a risk that a naive extraction, count, or classification would treat an unintended occurrence as the intended one.

参数：

- `reasoning: reasoning`：The agent text identifying that a value can play competing roles in the data and that misclassification is a risk.

成立条件：

- The reasoning points to a specific token, value, or record type that can appear in more than one role or context within the data.
- The reasoning states or clearly implies that confusing those occurrences would produce an incorrect extraction, count, or classification.
- The reasoning distinguishes the intended structured occurrence from the competing occurrence of the same token or value.

排除条件：

- The reasoning merely describes the data format without noting any competing role for a token or value.
- The reasoning selects a parsing or extraction rule without identifying any token that could be confused with another role.
- The ambiguity concerns the wording of the task or requirements rather than the content of the data.

### OBSERVATION_CONTRADICTS_EXPECTATION

签名：`OBSERVATION_CONTRADICTS_EXPECTATION(expectation_reasoning: reasoning, contradicting_observation: observation)`

The reasoning states, presupposes, or clearly implies a specific property, condition, format, or outcome that should hold, and the observation contains identifiable content showing that this expected condition does not hold.

参数：

- `expectation_reasoning: reasoning`：The agent text stating, presupposing, or clearly implying the property, condition, format, or outcome that should hold.
- `contradicting_observation: observation`：The observation containing content that shows the stated or implied expectation is violated.

成立条件：

- The reasoning states, presupposes, or clearly implies a specific expected property, condition, format, or outcome for the artifact, result, or state under consideration.
- The observation contains identifiable content showing that the expected property, condition, format, or outcome does not hold.

排除条件：

- The observation is consistent with, or confirms, the stated or implied expectation.
- The reasoning only registers uncertainty about the outcome and states no condition that is expected to hold.
- The difference between the observation and the expectation is not identifiable or bears on something other than the stated expectation.
- The reasoning draws its own explicit adverse judgment from the observation, which is a separate evaluation mechanism rather than an expectation-content contradiction.

### ASSERTS_TASK_COMPLETION

签名：`ASSERTS_TASK_COMPLETION(reasoning: reasoning)`

The reasoning makes a final claim that the overall task and its required deliverable have been completed, presenting completion as the concluded final state rather than as an intention, a plan, or an intermediate progress report.

参数：

- `reasoning: reasoning`：The reasoning node containing the final completion claim.

成立条件：

- The reasoning explicitly declares the task, or its required deliverable, complete, done, or finally achieved.
- The claim concerns the overall task outcome or its acceptance conditions rather than a single intermediate subtask.
- The statement is presented as a conclusion about the final state rather than as an intended future action or a progress report.

排除条件：

- The reasoning only describes intended future work, cleanup, or partial progress.
- The reasoning expresses unresolved uncertainty about whether the requirements have been met.
- The reasoning reports completion of a subtask without claiming overall task completion.
- The reasoning merely restates the task requirements without asserting that they have been satisfied.
