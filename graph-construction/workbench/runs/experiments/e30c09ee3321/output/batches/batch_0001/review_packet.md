# 第 1 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：1–5
Prompt 版本：v0001
本批新增谓词：26
本批已有谓词修订：0
当前谓词总数：26

## 二、本批新增谓词

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses at least one intended future action or a sequence of intended future actions that the agent commits to performing.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action or sequence of actions.

成立条件：

- The reasoning explicitly identifies at least one intended future action.
- The intended action is presented as something the agent will do next, rather than as a mere possibility or a restatement of the task.

排除条件：

- The reasoning only reports actions already completed.
- The reasoning only restates task requirements without committing to a future action.

### SPECIFIES_CORRECTIVE_CONTENT_WITH_JUSTIFICATION

签名：`SPECIFIES_CORRECTIVE_CONTENT_WITH_JUSTIFICATION(reasoning: reasoning)`

The reasoning supplies concrete content intended to correct, complete, or otherwise modify an artifact and justifies why that content satisfies the target requirement, optionally by evaluating and rejecting an alternative that would fail.

参数：

- `reasoning: reasoning`：The agent text that states the concrete replacement or completion content and the justification for its correctness.

成立条件：

- The reasoning states concrete content to be applied to the artifact, such as specific steps, replacement text, or a proof script, not merely the intention to change it.
- The reasoning explains why the stated content achieves the goal, using the semantics of the relevant domain entities.
- If alternative candidates are considered, at least one is rejected for an identified reason.

排除条件：

- The reasoning only describes the defect or goal without supplying concrete content to apply.
- The reasoning only lists generic strategies without indicating which one will be used or why it works.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning draws a conclusion using identifiable content of the observation as supporting evidence for that conclusion.

参数：

- `reasoning: reasoning`：The reasoning expressing the evidence-based conclusion.
- `observation: observation`：The observation supplying the evidence used for that conclusion.

成立条件：

- The reasoning states a conclusion that goes beyond restating the observation, such as a judgment about correctness, availability, or completion.
- Identifiable content of the observation, such as values, listed artifacts, returned text, or computed output, is used as support for that conclusion.

排除条件：

- The reasoning merely repeats or summarizes the observation without drawing a conclusion from it.
- The observation is unrelated to the conclusion or contains nothing that supports it.

### DIAGNOSES_FAILURE_AND_PRESCRIBES_CORRECTION

签名：`DIAGNOSES_FAILURE_AND_PRESCRIBES_CORRECTION(failure_observation: observation, diagnosis_reasoning: reasoning, corrective_action: action)`

An observation reports a failed outcome; the reasoning identifies a specific cause for the failure that links it to the semantics of the executed operation, and prescribes a corrective action that differs from the failed one in the diagnosed respect.

参数：

- `failure_observation: observation`：The observation reporting the error or unsuccessful outcome.
- `diagnosis_reasoning: reasoning`：The reasoning explaining the cause of the failure and specifying the corrected approach.
- `corrective_action: action`：The action that applies the corrected approach prescribed by the diagnosis.

成立条件：

- The observation reports an error or otherwise unsuccessful result.
- The reasoning states a specific cause for the failure rather than merely noting that it failed.
- The reasoning specifies how the operation must be changed in light of that cause.
- The corrective action implements that change and is therefore distinguishable from the failed action.

排除条件：

- The reasoning retries the same operation without identifying a cause or changing the approach.
- The reasoning speculates about causes unrelated to the reported error.
- The corrective action does not reflect the stated diagnosis.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(assumption_reasoning: reasoning, probe_action: action, probe_result: observation)`

A targeted action queries the environment to resolve a specific uncertainty or unverified prerequisite identified in reasoning, and the resulting observation provides evidence that settles or materially informs it before dependent work proceeds.

参数：

- `assumption_reasoning: reasoning`：The reasoning identifying the uncertainty or prerequisite that must be settled.
- `probe_action: action`：The action performing the targeted query about that uncertainty.
- `probe_result: observation`：The observation reporting the result relevant to the uncertainty.

成立条件：

- The reasoning identifies a specific open question or prerequisite condition whose value is not yet known.
- The probe action is directed at obtaining exactly that information from the environment.
- The observation returns information that resolves or materially informs the identified question.

排除条件：

- No identifiable uncertainty or prerequisite motivates the action.
- The action is unrelated to the stated question, or the observation does not address it.
- The probe merely repeats information already established earlier in the trajectory.

### VERIFIES_REQUIREMENT_SATISFACTION

签名：`VERIFIES_REQUIREMENT_SATISFACTION(verification_action: action, verification_observation: observation, concluding_reasoning: reasoning)`

After an outcome has been produced, a separate verification action inspects the produced artifact or result, its observation demonstrates the required property directly rather than only the absence of errors, and the reasoning concludes from it that the requirement is satisfied.

参数：

- `verification_action: action`：The action that inspects or exercises the already produced outcome.
- `verification_observation: observation`：The observation containing content that demonstrates the required property.
- `concluding_reasoning: reasoning`：The reasoning concluding that the requirement is met on the basis of that observation.

成立条件：

- The verification action is distinct from the action that produced the outcome and targets the produced artifact or result.
- The observation exposes content showing the required property actually holds, for example the resulting object is present and carries the expected content.
- The reasoning explicitly concludes that the requirement is satisfied, citing that observation.

排除条件：

- The action is the one that produced the outcome rather than an independent check of it.
- The observation only indicates that no error occurred, without demonstrating the required property.
- No conclusion is drawn from the observation, or the conclusion is not tied to it.

### ENUMERATES_REQUIRED_COMPONENTS

签名：`ENUMERATES_REQUIRED_COMPONENTS(reasoning: reasoning)`

The reasoning decomposes a stated goal into multiple distinct components, accounts, permissions, or artifacts that must exist for the goal to be satisfiable, turning the goal description into identifiable configuration obligations.

参数：

- `reasoning: reasoning`：The agent text listing the components or artifacts that must exist for the stated goal to be satisfiable.

成立条件：

- The reasoning identifies multiple distinct elements that must exist or be configured, such as an account, a repository, a deployment mechanism, or a serving process.
- Each identified element is justified by the goal's expected usage or by an explicit dependency of the goal rather than being listed arbitrarily.
- The enumeration includes required state, artifacts, or configuration obligations beyond merely ordering actions to perform.

排除条件：

- The reasoning only restates the goal without identifying required elements.
- The reasoning only gives an ordered procedure or action plan without identifying what must exist.
- The reasoning proposes only a single required element or an incidental detail.

### IMPLEMENTS_PLANNED_STEP

签名：`IMPLEMENTS_PLANNED_STEP(action: action, reasoning: reasoning)`

The action carries out a concrete operation or creates/configures an artifact that the reasoning explicitly identified as an intended step, so the action is the observable execution of a previously stated intention.

参数：

- `action: action`：The recorded tool invocation that performs the intended step.
- `reasoning: reasoning`：The reasoning that explicitly states the intended step which the action executes.

成立条件：

- The reasoning explicitly names the operation or artifact that the action then operates on before that action occurs.
- The action's content matches the intended step in purpose and target, not merely in topic.
- The action executes that intended step rather than an unrelated exploration.

排除条件：

- The action explores the environment without a corresponding previously stated intention.
- The reasoning mentions the operation or artifact only after the action's result is known.
- The action's target or purpose differs from the stated intention.

### ANTICIPATES_PROCEDURAL_PITFALL

签名：`ANTICIPATES_PROCEDURAL_PITFALL(reasoning: reasoning)`

The reasoning predicts a specific failure mode or unusable outcome that would arise from a default or naive procedure and states a preventive or corrective configuration measure derived from that prediction.

参数：

- `reasoning: reasoning`：The agent text that predicts the failure mode and states the preventive or corrective measure.

成立条件：

- The reasoning describes a concrete way the default or planned procedure could fail or produce an unusable result.
- The reasoning links that predicted failure to a preventive or corrective measure that changes the procedure or configuration.
- The predicted failure is prospective rather than an already observed error.

排除条件：

- The reasoning observes a failure that has already occurred rather than predicting one.
- The reasoning lists general best practices without linking them to an identified failure mode.
- The reasoning predicts a failure but does not state any measure addressing it.

### VALIDATES_BEFORE_ACTIVATION

签名：`VALIDATES_BEFORE_ACTIVATION(action: action, observation: observation)`

An action applies a configuration to a service or running system only after an explicit validity check of that configuration within the same invocation, and the observation reports both the successful validation and the activated or applied service.

参数：

- `action: action`：The tool invocation that performs the configuration validity check and then applies or activates the configuration.
- `observation: observation`：The tool result reporting the validation outcome and the activation or application state of the service.

成立条件：

- The action includes an explicit validation of the configuration before starting, reloading, or otherwise applying it.
- Activation or application is conditioned on that validation succeeding within the same invocation.
- The observation reports the validation as successful and shows the service running or the configuration applied.

排除条件：

- The service is started without any preceding configuration validation.
- Validation is performed but activation or application does not follow.
- The observation shows a validation failure or no evidence that the service is active or the configuration applied.
- Validation and activation occur in separate invocations, or the validation concerns an unrelated configuration.

### SIMULATES_END_USER_WORKFLOW

签名：`SIMULATES_END_USER_WORKFLOW(simulating_action: action, consumer_perspective_reasoning: reasoning)`

The action reproduces the operation sequence that an external consumer (the requester or a client) would perform against the assembled system, using throwaway credentials or scratch artifacts, in order to validate the system as it will be experienced by that consumer rather than to produce the final deliverable configuration.

参数：

- `simulating_action: action`：The tool invocation that executes the reproduced consumer-side operation sequence.
- `consumer_perspective_reasoning: reasoning`：Reasoning that frames the upcoming operation as acting like the requester or external client and explains that the sequence is a simulation for validation.

成立条件：

- The reasoning frames the upcoming operation as what the requester or an external client would do against the system.
- The action performs a multi-step sequence matching that consumer behavior, distinct from the configuration or installation steps that constitute the deliverable.
- The action relies on throwaway artifacts such as temporary credentials or scratch locations, so the simulation does not itself become part of the final state.
- The stated purpose is to exercise the system as a consumer would, not to build the deliverable.

排除条件：

- The action is an ordinary configuration or installation step that constitutes the deliverable itself.
- The action is a single isolated probe of one component rather than the consumer-visible operation sequence.
- The reasoning does not connect the action to consumer-side behavior.
- The action is not executed with throwaway artifacts and therefore permanently alters the delivered state.

### OBSERVATION_CONFIRMS_EXPECTED_OUTCOME

签名：`OBSERVATION_CONFIRMS_EXPECTED_OUTCOME(expectation_reasoning: reasoning, confirming_observation: observation)`

The observation reports exactly the result that the reasoning had predicted or required before the result was obtained, so the previously stated expectation can be judged satisfied rather than merely error-free.

参数：

- `expectation_reasoning: reasoning`：Reasoning stating the concrete expected or required outcome before the result is inspected.
- `confirming_observation: observation`：The tool result whose content corresponds to that expected outcome.

成立条件：

- The reasoning states a concrete expected outcome (a value, response, or state) before the corresponding observation is available.
- The observation contains content corresponding to that expectation, allowing the expectation to be judged satisfied rather than merely free of errors.

排除条件：

- The reasoning states no expected outcome, so the result cannot be judged against an expectation.
- The observation reports a different or partial result than the one expected.
- The observation is unrelated to the expectation expressed in the reasoning.
- The expectation is formulated only after the result has already been observed.

### RECOGNIZES_INCONCLUSIVE_TOOL_RESULT

签名：`RECOGNIZES_INCONCLUSIVE_TOOL_RESULT(reassessment_reasoning: reasoning, uninformative_observation: observation)`

The reasoning determines that an observation, although not reported as an error, fails to answer the question it was meant to answer because of a limitation of the method or tool used, and specifies a different method intended to obtain the missing information.

参数：

- `reassessment_reasoning: reasoning`：Reasoning that identifies the inadequacy of the earlier result, attributes it to a method limitation, and specifies an alternative method.
- `uninformative_observation: observation`：The observation whose output is empty, truncated, or otherwise uninformative for the intended question without being flagged as an error.

成立条件：

- The observation returned output that does not answer the intended question, and the observation is not flagged as an error.
- The reasoning attributes the missing information to a limitation of the command, tool, or method form used.
- The reasoning specifies a different command, option, or method intended to produce the missing information.

排除条件：

- The observation answers the question adequately, so no replacement method is needed.
- The observation reports an explicit failure that is diagnosed as a defect cause rather than a method limitation.
- The reasoning retries the identical method without changing it.
- The reasoning only notes that the output is empty without attributing it to a method limitation or proposing an alternative.

### RESTORES_PRISTINE_STATE_AFTER_TEST

签名：`RESTORES_PRISTINE_STATE_AFTER_TEST(cleanup_reasoning: reasoning, cleanup_actions: action[], state_observation: observation)`

Following verification or test activity, the agent deliberately removes or resets the artifacts created by that activity so the system returns to the state a later consumer expects to encounter before any such activity occurred.

参数：

- `cleanup_reasoning: reasoning`：Reasoning that enumerates the artifacts created during verification and states the target initial state to restore.
- `cleanup_actions: action[]`：The actions that delete, reset, or purge those artifacts; collectively they restore the pre-test state.
- `state_observation: observation`：The observation showing the post-cleanup state of the affected resources.

成立条件：

- The reasoning identifies artifacts created by the agent's own verification or test activity and states that they must be removed or reset to an initial state.
- The cleanup actions delete, reset, or empty those identified artifacts.
- The state observation shows the affected resources emptied or matching the intended initial configuration.

排除条件：

- No artifacts were created by the agent's own verification activity, so there is nothing to restore.
- The cleanup leaves the identified artifacts in place, or the observation shows them still present because the removal failed.
- The deletion is part of ordinary construction rather than restoring a state that a later consumer should encounter.

### VERIFIES_RUNTIME_SERVICE_STATE

签名：`VERIFIES_RUNTIME_SERVICE_STATE(inspection_action: action, runtime_observation: observation)`

An inspection action queries the actual runtime state of deployed services, such as running processes, listening sockets, or an exercised endpoint, and the observation shows the intended services active at the intended endpoints.

参数：

- `inspection_action: action`：The tool invocation that queries the running state of the deployed services.
- `runtime_observation: observation`：The tool result listing processes, listening addresses, or endpoint responses that reveal the services' actual runtime state.

成立条件：

- The action queries the actual running state of the services (processes, sockets, or an exercised endpoint) rather than only the content of their configuration files.
- The observation reports the intended services present and active, with the expected endpoints or listening addresses visible.

排除条件：

- The action modifies configuration or starts services instead of inspecting runtime state.
- The observation only shows configuration syntax validity without any evidence of running state.
- The observation shows the service absent or not listening on the intended endpoint.
- The observation concerns a resource unrelated to the deployed services.

### ADDS_AVAILABILITY_SAFEGUARD

签名：`ADDS_AVAILABILITY_SAFEGUARD(safeguard_reasoning: reasoning, safeguard_action: action)`

The agent installs a recovery mechanism that restores a component's availability when it is later found stopped, motivated by anticipated future interruptions or restarts rather than by the needs of the immediate request.

参数：

- `safeguard_reasoning: reasoning`：Reasoning that motivates the extra recovery mechanism as protection against future interruptions or restarts.
- `safeguard_action: action`：The tool invocation that creates or installs the recovery mechanism.

成立条件：

- The reasoning frames the addition as protection against a future interruption, restart, or unavailability rather than as a step needed for the current request to work.
- The action creates or installs a mechanism that checks whether the component is present and restarts or restores it when absent.
- The mechanism is designed to be safe to invoke repeatedly, so it can act as an automatic safeguard.

排除条件：

- The action is ordinary service startup required for the current request to work at all.
- The mechanism cannot restore a stopped component or would fail the calling shell on error.
- No reasoning connects the mechanism to future availability concerns.
- The installed mechanism only reports status without restoring the component.

### DECLARES_TASK_COMPLETE

签名：`DECLARES_TASK_COMPLETE(reasoning: reasoning)`

The reasoning asserts that the overall goal of the task has been achieved and supports that claim by summarizing or enumerating the delivered components, configuration, or verified outcomes, rather than reporting only that one isolated step succeeded.

参数：

- `reasoning: reasoning`：The agent text concluding that the overall task is finished and summarizing or enumerating what was delivered or verified.

成立条件：

- The reasoning explicitly asserts that the overall task or goal is complete.
- The completion claim is accompanied by a summary or enumeration of the delivered components, configuration state, or verified outcomes.

排除条件：

- The reasoning reports only an intermediate step's success without claiming overall completion.
- The reasoning expresses an intention to finish later rather than asserting that the task is finished.

### EXPLAINS_ANOMALOUS_OBSERVATION

签名：`EXPLAINS_ANOMALOUS_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning treats a recorded observation as anomalous — empty, absent, unexpected, or inconsistent with the check that produced it — and attributes the anomaly to a specific identifiable mechanism, so the anomalous content is not taken at face value as evidence about the condition the check was designed to reveal.

参数：

- `reasoning: reasoning`：The agent text that flags the result as unexpected, empty, or absent and proposes a specific explanation for it.
- `observation: observation`：The observation whose output is empty, missing, unexpected, or otherwise inconsistent with the intent of the action that produced it.

成立条件：

- The reasoning explicitly notes that the observation's result is empty, missing, unexpected, or otherwise not what the check was designed to reveal.
- The reasoning attributes the anomaly to an identifiable mechanism, such as a limitation of the command or tool form, an unfollowed link, or an artifact of how the process was launched.
- The reasoning thereby reinterprets the anomalous result so that it is not automatically treated as evidence against the condition under investigation.

排除条件：

- The reasoning reads the observation at face value as evidence about the condition it was meant to check.
- The reasoning reports the unexpected or empty result without offering any causal explanation.
- The reasoning attributes the result only to a generic failure without identifying a mechanism.

### AUDITS_STATE_AGAINST_ENUMERATED_CRITERIA

签名：`AUDITS_STATE_AGAINST_ENUMERATED_CRITERIA(criteria_reasoning: reasoning, audit_action: action, audit_result: observation)`

The reasoning enumerates multiple independent conditions that must hold for success, a single action collects evidence for those conditions in one combined inspection, and the observation reports state values that can be matched against the enumerated conditions.

参数：

- `criteria_reasoning: reasoning`：The reasoning enumerating the multiple independent conditions or state facts to be audited.
- `audit_action: action`：The action that gathers state evidence for the enumerated conditions in one combined inspection.
- `audit_result: observation`：The observation reporting state values or findings that correspond to the enumerated conditions, including any gaps.

成立条件：

- The reasoning explicitly enumerates two or more distinct conditions or state facts that must hold for success.
- The action collects evidence for those conditions within a single combined inspection rather than one check per condition.
- The observation reports values or findings that can be matched one-to-one against the enumerated conditions.

排除条件：

- The reasoning checks only a single condition.
- The observation does not report on the enumerated conditions, so the result cannot be matched against them.
- No criteria are stated before the inspection, so the result cannot be judged against them.

### INSPECTS_STATE_WITHOUT_MODIFICATION

签名：`INSPECTS_STATE_WITHOUT_MODIFICATION(inspection_action: action)`

The action only reads or queries pre-existing system state — processes, sockets, files, references, permissions, or an exercised endpoint — and does not itself create, modify, or delete persistent configuration, file content, or data.

参数：

- `inspection_action: action`：The action that reads or queries existing state for evidence gathering.

成立条件：

- The action's arguments consist of read-only queries against state that already exists in the environment.
- No persistent configuration, file content, or data is created, modified, or deleted by the action.
- The purpose of the action is to obtain information about the environment rather than to change it.

排除条件：

- The action writes, appends, deletes, or otherwise changes persistent state.
- The action both inspects and mutates state within the same invocation, so persistent state differs after it runs.

### SEPARATES_HARD_CONSTRAINTS_FROM_SOFT_PREFERENCES

签名：`SEPARATES_HARD_CONSTRAINTS_FROM_SOFT_PREFERENCES(constraint_reasoning: reasoning)`

The reasoning classifies the requirements bearing on a solution into binding constraints that any acceptable solution must satisfy and soft preferences that may be used only to rank or tie-break among solutions that already satisfy those binding constraints, and states or applies that precedence.

参数：

- `constraint_reasoning: reasoning`：The reasoning that classifies requirements by force and establishes how binding constraints and soft preferences are to be applied.

成立条件：

- The reasoning identifies at least one requirement as binding, i.e., a condition whose violation disqualifies a candidate solution.
- The reasoning identifies at least one requirement as a soft preference that is optional or of lower priority.
- The reasoning states or applies the precedence that binding constraints filter acceptable solutions before preferences are used to choose among the survivors.

排除条件：

- All requirements are treated as equally binding, or all are treated as optional, so no distinction in force is drawn.
- The reasoning lists requirements without indicating which are mandatory and which are merely preferred.
- A preference is allowed to admit a solution that violates a binding constraint, or a binding constraint is treated as negotiable.

### AGGREGATES_MULTIPLE_OBSERVATIONS_INTO_JOINT_CONSTRAINT

签名：`AGGREGATES_MULTIPLE_OBSERVATIONS_INTO_JOINT_CONSTRAINT(synthesis_reasoning: reasoning, source_observations: observation[])`

The reasoning merges the content of multiple observations into a single joint constraint or shared model that every acceptable solution must satisfy collectively with respect to all represented entities, instead of treating each observation as an independent local fact.

参数：

- `synthesis_reasoning: reasoning`：The reasoning that combines content from multiple observations into one joint constraint or shared model.
- `source_observations: observation[]`：The observations whose contents are collectively combined into the shared constraint or model; support is collective, requiring at least two contributors.

成立条件：

- At least two observations supply relevant source content.
- The reasoning explicitly combines (unions, merges, or aggregates) that content into one joint constraint or shared model.
- The joint constraint is applied collectively to all entities represented by those observations, so no solution may satisfy it while violating any single observation's content.

排除条件：

- The observation contents are used only separately or locally, without forming a shared constraint or model.
- Only one observation contributes relevant content.
- The reasoning merely lists the observations without combining them into a constraint or model.

### RESOLVES_OBSERVED_INCONSISTENCY_CONSERVATIVELY

签名：`RESOLVES_OBSERVED_INCONSISTENCY_CONSERVATIVELY(resolution_reasoning: reasoning, observation: observation)`

The reasoning detects a discrepancy in observed data relative to labels, expectations, or assumed structure, weighs plausible interpretations of that discrepancy, and adopts an interpretation or working assumption that remains valid under the plausible alternatives rather than committing to a single unverified reading.

参数：

- `resolution_reasoning: reasoning`：The reasoning that notices the discrepancy, evaluates plausible interpretations, and adopts a resolution valid under those alternatives.
- `observation: observation`：The observed data whose content conflicts with labels, expectations, or assumed structure.

成立条件：

- The observation's content conflicts with labels, expected structure, or prior assumptions, and the reasoning explicitly notices the conflict.
- The reasoning considers more than one plausible interpretation of the discrepancy.
- The reasoning adopts a resolution or working assumption that stays valid under the plausible alternatives.

排除条件：

- The reasoning does not notice the discrepancy or takes the observation at face value.
- The discrepancy is noted but is irrelevant to the interpretation actually adopted.
- An interpretation is adopted without considering plausible alternatives, so the resolution is not conservative.

### SELECTS_OPTIMAL_CANDIDATE_BY_EXPLICIT_ORDERING

签名：`SELECTS_OPTIMAL_CANDIDATE_BY_EXPLICIT_ORDERING(selection_reasoning: reasoning)`

The reasoning enumerates or compares multiple candidate solutions, eliminates those that violate binding constraints, and selects from the survivors the candidate that is optimal under an explicit ordering or extremum criterion (such as earliest, cheapest, or smallest) that the reasoning states or applies.

参数：

- `selection_reasoning: reasoning`：The reasoning that compares candidates, eliminates constraint-violating ones, and selects an optimal survivor according to a stated ordering.

成立条件：

- Multiple candidate solutions are enumerated or compared.
- Candidates that violate one or more binding constraints are eliminated, either explicitly or by a stated filtering rule.
- An explicit ordering or extremum criterion is stated or applied to the surviving candidates.
- The selected candidate is the optimal survivor under that criterion.

排除条件：

- Only one candidate is considered, so no comparison or ordering is applied.
- The choice is arbitrary or rests on no stated ordering criterion.
- No candidate is excluded on constraint grounds.
- The stated ordering is not the basis of the final choice.

### PREPARES_VALIDATION_PROCEDURE

签名：`PREPARES_VALIDATION_PROCEDURE(validation_plan_reasoning: reasoning, procedure_creation_action: action)`

The reasoning specifies checks or expected conditions against which a produced solution is to be validated, and the action creates a reusable test or check procedure that embodies those checks so the solution can later be assessed against them.

参数：

- `validation_plan_reasoning: reasoning`：The reasoning that specifies the checks or expected conditions for validating the produced solution.
- `procedure_creation_action: action`：The action that creates the test or check procedure embodying those validation criteria.

成立条件：

- The reasoning enumerates concrete checks or expected conditions for validating the produced solution.
- The action creates a procedure (script, test, or checklist) that embodies those checks.
- The created procedure is intended to assess the produced solution against the stated requirements rather than to constitute the solution itself.

排除条件：

- The action creates or modifies the deliverable solution rather than a procedure for checking it.
- No concrete checks or expected conditions are specified before the procedure is created.
- The created procedure does not embody the stated validation checks.

### VERIFIES_INPUT_INTEGRITY

签名：`VERIFIES_INPUT_INTEGRITY(integrity_check_action: action, integrity_evidence_observation: observation, integrity_conclusion_reasoning: reasoning)`

Motivated by a requirement that input resources remain unmodified, an action retrieves metadata, checksums, or listings for those inputs, the observation supplies that integrity evidence, and the reasoning concludes from it that the inputs were not altered.

参数：

- `integrity_check_action: action`：The action that retrieves metadata, checksums, or listings for the input resources without modifying them.
- `integrity_evidence_observation: observation`：The observation containing the retrieved metadata, checksums, listings, or comparable evidence about input integrity.
- `integrity_conclusion_reasoning: reasoning`：The reasoning that concludes from the evidence that the input resources were not altered.

成立条件：

- A requirement or concern exists that the input resources must remain unmodified.
- The action retrieves metadata, checksums, listings, or comparable evidence about those inputs without modifying them.
- The observation supplies the retrieved integrity evidence.
- The reasoning concludes, on the basis of that evidence, that the inputs were not altered.

排除条件：

- No requirement or concern about input integrity is present.
- The action modifies the inputs or targets resources other than the inputs.
- The observation provides no evidence bearing on whether the inputs changed.
- The conclusion is asserted without reference to the evidence.

## 三、本批已有谓词修订

本批没有修订已有谓词。

## 四、当前完整 Registry

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning explicitly expresses at least one intended future action or a sequence of intended future actions that the agent commits to performing.

参数：

- `reasoning: reasoning`：The agent text expressing the intended future action or sequence of actions.

成立条件：

- The reasoning explicitly identifies at least one intended future action.
- The intended action is presented as something the agent will do next, rather than as a mere possibility or a restatement of the task.

排除条件：

- The reasoning only reports actions already completed.
- The reasoning only restates task requirements without committing to a future action.

### SPECIFIES_CORRECTIVE_CONTENT_WITH_JUSTIFICATION

签名：`SPECIFIES_CORRECTIVE_CONTENT_WITH_JUSTIFICATION(reasoning: reasoning)`

The reasoning supplies concrete content intended to correct, complete, or otherwise modify an artifact and justifies why that content satisfies the target requirement, optionally by evaluating and rejecting an alternative that would fail.

参数：

- `reasoning: reasoning`：The agent text that states the concrete replacement or completion content and the justification for its correctness.

成立条件：

- The reasoning states concrete content to be applied to the artifact, such as specific steps, replacement text, or a proof script, not merely the intention to change it.
- The reasoning explains why the stated content achieves the goal, using the semantics of the relevant domain entities.
- If alternative candidates are considered, at least one is rejected for an identified reason.

排除条件：

- The reasoning only describes the defect or goal without supplying concrete content to apply.
- The reasoning only lists generic strategies without indicating which one will be used or why it works.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning draws a conclusion using identifiable content of the observation as supporting evidence for that conclusion.

参数：

- `reasoning: reasoning`：The reasoning expressing the evidence-based conclusion.
- `observation: observation`：The observation supplying the evidence used for that conclusion.

成立条件：

- The reasoning states a conclusion that goes beyond restating the observation, such as a judgment about correctness, availability, or completion.
- Identifiable content of the observation, such as values, listed artifacts, returned text, or computed output, is used as support for that conclusion.

排除条件：

- The reasoning merely repeats or summarizes the observation without drawing a conclusion from it.
- The observation is unrelated to the conclusion or contains nothing that supports it.

### DIAGNOSES_FAILURE_AND_PRESCRIBES_CORRECTION

签名：`DIAGNOSES_FAILURE_AND_PRESCRIBES_CORRECTION(failure_observation: observation, diagnosis_reasoning: reasoning, corrective_action: action)`

An observation reports a failed outcome; the reasoning identifies a specific cause for the failure that links it to the semantics of the executed operation, and prescribes a corrective action that differs from the failed one in the diagnosed respect.

参数：

- `failure_observation: observation`：The observation reporting the error or unsuccessful outcome.
- `diagnosis_reasoning: reasoning`：The reasoning explaining the cause of the failure and specifying the corrected approach.
- `corrective_action: action`：The action that applies the corrected approach prescribed by the diagnosis.

成立条件：

- The observation reports an error or otherwise unsuccessful result.
- The reasoning states a specific cause for the failure rather than merely noting that it failed.
- The reasoning specifies how the operation must be changed in light of that cause.
- The corrective action implements that change and is therefore distinguishable from the failed action.

排除条件：

- The reasoning retries the same operation without identifying a cause or changing the approach.
- The reasoning speculates about causes unrelated to the reported error.
- The corrective action does not reflect the stated diagnosis.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(assumption_reasoning: reasoning, probe_action: action, probe_result: observation)`

A targeted action queries the environment to resolve a specific uncertainty or unverified prerequisite identified in reasoning, and the resulting observation provides evidence that settles or materially informs it before dependent work proceeds.

参数：

- `assumption_reasoning: reasoning`：The reasoning identifying the uncertainty or prerequisite that must be settled.
- `probe_action: action`：The action performing the targeted query about that uncertainty.
- `probe_result: observation`：The observation reporting the result relevant to the uncertainty.

成立条件：

- The reasoning identifies a specific open question or prerequisite condition whose value is not yet known.
- The probe action is directed at obtaining exactly that information from the environment.
- The observation returns information that resolves or materially informs the identified question.

排除条件：

- No identifiable uncertainty or prerequisite motivates the action.
- The action is unrelated to the stated question, or the observation does not address it.
- The probe merely repeats information already established earlier in the trajectory.

### VERIFIES_REQUIREMENT_SATISFACTION

签名：`VERIFIES_REQUIREMENT_SATISFACTION(verification_action: action, verification_observation: observation, concluding_reasoning: reasoning)`

After an outcome has been produced, a separate verification action inspects the produced artifact or result, its observation demonstrates the required property directly rather than only the absence of errors, and the reasoning concludes from it that the requirement is satisfied.

参数：

- `verification_action: action`：The action that inspects or exercises the already produced outcome.
- `verification_observation: observation`：The observation containing content that demonstrates the required property.
- `concluding_reasoning: reasoning`：The reasoning concluding that the requirement is met on the basis of that observation.

成立条件：

- The verification action is distinct from the action that produced the outcome and targets the produced artifact or result.
- The observation exposes content showing the required property actually holds, for example the resulting object is present and carries the expected content.
- The reasoning explicitly concludes that the requirement is satisfied, citing that observation.

排除条件：

- The action is the one that produced the outcome rather than an independent check of it.
- The observation only indicates that no error occurred, without demonstrating the required property.
- No conclusion is drawn from the observation, or the conclusion is not tied to it.

### ENUMERATES_REQUIRED_COMPONENTS

签名：`ENUMERATES_REQUIRED_COMPONENTS(reasoning: reasoning)`

The reasoning decomposes a stated goal into multiple distinct components, accounts, permissions, or artifacts that must exist for the goal to be satisfiable, turning the goal description into identifiable configuration obligations.

参数：

- `reasoning: reasoning`：The agent text listing the components or artifacts that must exist for the stated goal to be satisfiable.

成立条件：

- The reasoning identifies multiple distinct elements that must exist or be configured, such as an account, a repository, a deployment mechanism, or a serving process.
- Each identified element is justified by the goal's expected usage or by an explicit dependency of the goal rather than being listed arbitrarily.
- The enumeration includes required state, artifacts, or configuration obligations beyond merely ordering actions to perform.

排除条件：

- The reasoning only restates the goal without identifying required elements.
- The reasoning only gives an ordered procedure or action plan without identifying what must exist.
- The reasoning proposes only a single required element or an incidental detail.

### IMPLEMENTS_PLANNED_STEP

签名：`IMPLEMENTS_PLANNED_STEP(action: action, reasoning: reasoning)`

The action carries out a concrete operation or creates/configures an artifact that the reasoning explicitly identified as an intended step, so the action is the observable execution of a previously stated intention.

参数：

- `action: action`：The recorded tool invocation that performs the intended step.
- `reasoning: reasoning`：The reasoning that explicitly states the intended step which the action executes.

成立条件：

- The reasoning explicitly names the operation or artifact that the action then operates on before that action occurs.
- The action's content matches the intended step in purpose and target, not merely in topic.
- The action executes that intended step rather than an unrelated exploration.

排除条件：

- The action explores the environment without a corresponding previously stated intention.
- The reasoning mentions the operation or artifact only after the action's result is known.
- The action's target or purpose differs from the stated intention.

### ANTICIPATES_PROCEDURAL_PITFALL

签名：`ANTICIPATES_PROCEDURAL_PITFALL(reasoning: reasoning)`

The reasoning predicts a specific failure mode or unusable outcome that would arise from a default or naive procedure and states a preventive or corrective configuration measure derived from that prediction.

参数：

- `reasoning: reasoning`：The agent text that predicts the failure mode and states the preventive or corrective measure.

成立条件：

- The reasoning describes a concrete way the default or planned procedure could fail or produce an unusable result.
- The reasoning links that predicted failure to a preventive or corrective measure that changes the procedure or configuration.
- The predicted failure is prospective rather than an already observed error.

排除条件：

- The reasoning observes a failure that has already occurred rather than predicting one.
- The reasoning lists general best practices without linking them to an identified failure mode.
- The reasoning predicts a failure but does not state any measure addressing it.

### VALIDATES_BEFORE_ACTIVATION

签名：`VALIDATES_BEFORE_ACTIVATION(action: action, observation: observation)`

An action applies a configuration to a service or running system only after an explicit validity check of that configuration within the same invocation, and the observation reports both the successful validation and the activated or applied service.

参数：

- `action: action`：The tool invocation that performs the configuration validity check and then applies or activates the configuration.
- `observation: observation`：The tool result reporting the validation outcome and the activation or application state of the service.

成立条件：

- The action includes an explicit validation of the configuration before starting, reloading, or otherwise applying it.
- Activation or application is conditioned on that validation succeeding within the same invocation.
- The observation reports the validation as successful and shows the service running or the configuration applied.

排除条件：

- The service is started without any preceding configuration validation.
- Validation is performed but activation or application does not follow.
- The observation shows a validation failure or no evidence that the service is active or the configuration applied.
- Validation and activation occur in separate invocations, or the validation concerns an unrelated configuration.

### SIMULATES_END_USER_WORKFLOW

签名：`SIMULATES_END_USER_WORKFLOW(simulating_action: action, consumer_perspective_reasoning: reasoning)`

The action reproduces the operation sequence that an external consumer (the requester or a client) would perform against the assembled system, using throwaway credentials or scratch artifacts, in order to validate the system as it will be experienced by that consumer rather than to produce the final deliverable configuration.

参数：

- `simulating_action: action`：The tool invocation that executes the reproduced consumer-side operation sequence.
- `consumer_perspective_reasoning: reasoning`：Reasoning that frames the upcoming operation as acting like the requester or external client and explains that the sequence is a simulation for validation.

成立条件：

- The reasoning frames the upcoming operation as what the requester or an external client would do against the system.
- The action performs a multi-step sequence matching that consumer behavior, distinct from the configuration or installation steps that constitute the deliverable.
- The action relies on throwaway artifacts such as temporary credentials or scratch locations, so the simulation does not itself become part of the final state.
- The stated purpose is to exercise the system as a consumer would, not to build the deliverable.

排除条件：

- The action is an ordinary configuration or installation step that constitutes the deliverable itself.
- The action is a single isolated probe of one component rather than the consumer-visible operation sequence.
- The reasoning does not connect the action to consumer-side behavior.
- The action is not executed with throwaway artifacts and therefore permanently alters the delivered state.

### OBSERVATION_CONFIRMS_EXPECTED_OUTCOME

签名：`OBSERVATION_CONFIRMS_EXPECTED_OUTCOME(expectation_reasoning: reasoning, confirming_observation: observation)`

The observation reports exactly the result that the reasoning had predicted or required before the result was obtained, so the previously stated expectation can be judged satisfied rather than merely error-free.

参数：

- `expectation_reasoning: reasoning`：Reasoning stating the concrete expected or required outcome before the result is inspected.
- `confirming_observation: observation`：The tool result whose content corresponds to that expected outcome.

成立条件：

- The reasoning states a concrete expected outcome (a value, response, or state) before the corresponding observation is available.
- The observation contains content corresponding to that expectation, allowing the expectation to be judged satisfied rather than merely free of errors.

排除条件：

- The reasoning states no expected outcome, so the result cannot be judged against an expectation.
- The observation reports a different or partial result than the one expected.
- The observation is unrelated to the expectation expressed in the reasoning.
- The expectation is formulated only after the result has already been observed.

### RECOGNIZES_INCONCLUSIVE_TOOL_RESULT

签名：`RECOGNIZES_INCONCLUSIVE_TOOL_RESULT(reassessment_reasoning: reasoning, uninformative_observation: observation)`

The reasoning determines that an observation, although not reported as an error, fails to answer the question it was meant to answer because of a limitation of the method or tool used, and specifies a different method intended to obtain the missing information.

参数：

- `reassessment_reasoning: reasoning`：Reasoning that identifies the inadequacy of the earlier result, attributes it to a method limitation, and specifies an alternative method.
- `uninformative_observation: observation`：The observation whose output is empty, truncated, or otherwise uninformative for the intended question without being flagged as an error.

成立条件：

- The observation returned output that does not answer the intended question, and the observation is not flagged as an error.
- The reasoning attributes the missing information to a limitation of the command, tool, or method form used.
- The reasoning specifies a different command, option, or method intended to produce the missing information.

排除条件：

- The observation answers the question adequately, so no replacement method is needed.
- The observation reports an explicit failure that is diagnosed as a defect cause rather than a method limitation.
- The reasoning retries the identical method without changing it.
- The reasoning only notes that the output is empty without attributing it to a method limitation or proposing an alternative.

### RESTORES_PRISTINE_STATE_AFTER_TEST

签名：`RESTORES_PRISTINE_STATE_AFTER_TEST(cleanup_reasoning: reasoning, cleanup_actions: action[], state_observation: observation)`

Following verification or test activity, the agent deliberately removes or resets the artifacts created by that activity so the system returns to the state a later consumer expects to encounter before any such activity occurred.

参数：

- `cleanup_reasoning: reasoning`：Reasoning that enumerates the artifacts created during verification and states the target initial state to restore.
- `cleanup_actions: action[]`：The actions that delete, reset, or purge those artifacts; collectively they restore the pre-test state.
- `state_observation: observation`：The observation showing the post-cleanup state of the affected resources.

成立条件：

- The reasoning identifies artifacts created by the agent's own verification or test activity and states that they must be removed or reset to an initial state.
- The cleanup actions delete, reset, or empty those identified artifacts.
- The state observation shows the affected resources emptied or matching the intended initial configuration.

排除条件：

- No artifacts were created by the agent's own verification activity, so there is nothing to restore.
- The cleanup leaves the identified artifacts in place, or the observation shows them still present because the removal failed.
- The deletion is part of ordinary construction rather than restoring a state that a later consumer should encounter.

### VERIFIES_RUNTIME_SERVICE_STATE

签名：`VERIFIES_RUNTIME_SERVICE_STATE(inspection_action: action, runtime_observation: observation)`

An inspection action queries the actual runtime state of deployed services, such as running processes, listening sockets, or an exercised endpoint, and the observation shows the intended services active at the intended endpoints.

参数：

- `inspection_action: action`：The tool invocation that queries the running state of the deployed services.
- `runtime_observation: observation`：The tool result listing processes, listening addresses, or endpoint responses that reveal the services' actual runtime state.

成立条件：

- The action queries the actual running state of the services (processes, sockets, or an exercised endpoint) rather than only the content of their configuration files.
- The observation reports the intended services present and active, with the expected endpoints or listening addresses visible.

排除条件：

- The action modifies configuration or starts services instead of inspecting runtime state.
- The observation only shows configuration syntax validity without any evidence of running state.
- The observation shows the service absent or not listening on the intended endpoint.
- The observation concerns a resource unrelated to the deployed services.

### ADDS_AVAILABILITY_SAFEGUARD

签名：`ADDS_AVAILABILITY_SAFEGUARD(safeguard_reasoning: reasoning, safeguard_action: action)`

The agent installs a recovery mechanism that restores a component's availability when it is later found stopped, motivated by anticipated future interruptions or restarts rather than by the needs of the immediate request.

参数：

- `safeguard_reasoning: reasoning`：Reasoning that motivates the extra recovery mechanism as protection against future interruptions or restarts.
- `safeguard_action: action`：The tool invocation that creates or installs the recovery mechanism.

成立条件：

- The reasoning frames the addition as protection against a future interruption, restart, or unavailability rather than as a step needed for the current request to work.
- The action creates or installs a mechanism that checks whether the component is present and restarts or restores it when absent.
- The mechanism is designed to be safe to invoke repeatedly, so it can act as an automatic safeguard.

排除条件：

- The action is ordinary service startup required for the current request to work at all.
- The mechanism cannot restore a stopped component or would fail the calling shell on error.
- No reasoning connects the mechanism to future availability concerns.
- The installed mechanism only reports status without restoring the component.

### DECLARES_TASK_COMPLETE

签名：`DECLARES_TASK_COMPLETE(reasoning: reasoning)`

The reasoning asserts that the overall goal of the task has been achieved and supports that claim by summarizing or enumerating the delivered components, configuration, or verified outcomes, rather than reporting only that one isolated step succeeded.

参数：

- `reasoning: reasoning`：The agent text concluding that the overall task is finished and summarizing or enumerating what was delivered or verified.

成立条件：

- The reasoning explicitly asserts that the overall task or goal is complete.
- The completion claim is accompanied by a summary or enumeration of the delivered components, configuration state, or verified outcomes.

排除条件：

- The reasoning reports only an intermediate step's success without claiming overall completion.
- The reasoning expresses an intention to finish later rather than asserting that the task is finished.

### EXPLAINS_ANOMALOUS_OBSERVATION

签名：`EXPLAINS_ANOMALOUS_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning treats a recorded observation as anomalous — empty, absent, unexpected, or inconsistent with the check that produced it — and attributes the anomaly to a specific identifiable mechanism, so the anomalous content is not taken at face value as evidence about the condition the check was designed to reveal.

参数：

- `reasoning: reasoning`：The agent text that flags the result as unexpected, empty, or absent and proposes a specific explanation for it.
- `observation: observation`：The observation whose output is empty, missing, unexpected, or otherwise inconsistent with the intent of the action that produced it.

成立条件：

- The reasoning explicitly notes that the observation's result is empty, missing, unexpected, or otherwise not what the check was designed to reveal.
- The reasoning attributes the anomaly to an identifiable mechanism, such as a limitation of the command or tool form, an unfollowed link, or an artifact of how the process was launched.
- The reasoning thereby reinterprets the anomalous result so that it is not automatically treated as evidence against the condition under investigation.

排除条件：

- The reasoning reads the observation at face value as evidence about the condition it was meant to check.
- The reasoning reports the unexpected or empty result without offering any causal explanation.
- The reasoning attributes the result only to a generic failure without identifying a mechanism.

### AUDITS_STATE_AGAINST_ENUMERATED_CRITERIA

签名：`AUDITS_STATE_AGAINST_ENUMERATED_CRITERIA(criteria_reasoning: reasoning, audit_action: action, audit_result: observation)`

The reasoning enumerates multiple independent conditions that must hold for success, a single action collects evidence for those conditions in one combined inspection, and the observation reports state values that can be matched against the enumerated conditions.

参数：

- `criteria_reasoning: reasoning`：The reasoning enumerating the multiple independent conditions or state facts to be audited.
- `audit_action: action`：The action that gathers state evidence for the enumerated conditions in one combined inspection.
- `audit_result: observation`：The observation reporting state values or findings that correspond to the enumerated conditions, including any gaps.

成立条件：

- The reasoning explicitly enumerates two or more distinct conditions or state facts that must hold for success.
- The action collects evidence for those conditions within a single combined inspection rather than one check per condition.
- The observation reports values or findings that can be matched one-to-one against the enumerated conditions.

排除条件：

- The reasoning checks only a single condition.
- The observation does not report on the enumerated conditions, so the result cannot be matched against them.
- No criteria are stated before the inspection, so the result cannot be judged against them.

### INSPECTS_STATE_WITHOUT_MODIFICATION

签名：`INSPECTS_STATE_WITHOUT_MODIFICATION(inspection_action: action)`

The action only reads or queries pre-existing system state — processes, sockets, files, references, permissions, or an exercised endpoint — and does not itself create, modify, or delete persistent configuration, file content, or data.

参数：

- `inspection_action: action`：The action that reads or queries existing state for evidence gathering.

成立条件：

- The action's arguments consist of read-only queries against state that already exists in the environment.
- No persistent configuration, file content, or data is created, modified, or deleted by the action.
- The purpose of the action is to obtain information about the environment rather than to change it.

排除条件：

- The action writes, appends, deletes, or otherwise changes persistent state.
- The action both inspects and mutates state within the same invocation, so persistent state differs after it runs.

### SEPARATES_HARD_CONSTRAINTS_FROM_SOFT_PREFERENCES

签名：`SEPARATES_HARD_CONSTRAINTS_FROM_SOFT_PREFERENCES(constraint_reasoning: reasoning)`

The reasoning classifies the requirements bearing on a solution into binding constraints that any acceptable solution must satisfy and soft preferences that may be used only to rank or tie-break among solutions that already satisfy those binding constraints, and states or applies that precedence.

参数：

- `constraint_reasoning: reasoning`：The reasoning that classifies requirements by force and establishes how binding constraints and soft preferences are to be applied.

成立条件：

- The reasoning identifies at least one requirement as binding, i.e., a condition whose violation disqualifies a candidate solution.
- The reasoning identifies at least one requirement as a soft preference that is optional or of lower priority.
- The reasoning states or applies the precedence that binding constraints filter acceptable solutions before preferences are used to choose among the survivors.

排除条件：

- All requirements are treated as equally binding, or all are treated as optional, so no distinction in force is drawn.
- The reasoning lists requirements without indicating which are mandatory and which are merely preferred.
- A preference is allowed to admit a solution that violates a binding constraint, or a binding constraint is treated as negotiable.

### AGGREGATES_MULTIPLE_OBSERVATIONS_INTO_JOINT_CONSTRAINT

签名：`AGGREGATES_MULTIPLE_OBSERVATIONS_INTO_JOINT_CONSTRAINT(synthesis_reasoning: reasoning, source_observations: observation[])`

The reasoning merges the content of multiple observations into a single joint constraint or shared model that every acceptable solution must satisfy collectively with respect to all represented entities, instead of treating each observation as an independent local fact.

参数：

- `synthesis_reasoning: reasoning`：The reasoning that combines content from multiple observations into one joint constraint or shared model.
- `source_observations: observation[]`：The observations whose contents are collectively combined into the shared constraint or model; support is collective, requiring at least two contributors.

成立条件：

- At least two observations supply relevant source content.
- The reasoning explicitly combines (unions, merges, or aggregates) that content into one joint constraint or shared model.
- The joint constraint is applied collectively to all entities represented by those observations, so no solution may satisfy it while violating any single observation's content.

排除条件：

- The observation contents are used only separately or locally, without forming a shared constraint or model.
- Only one observation contributes relevant content.
- The reasoning merely lists the observations without combining them into a constraint or model.

### RESOLVES_OBSERVED_INCONSISTENCY_CONSERVATIVELY

签名：`RESOLVES_OBSERVED_INCONSISTENCY_CONSERVATIVELY(resolution_reasoning: reasoning, observation: observation)`

The reasoning detects a discrepancy in observed data relative to labels, expectations, or assumed structure, weighs plausible interpretations of that discrepancy, and adopts an interpretation or working assumption that remains valid under the plausible alternatives rather than committing to a single unverified reading.

参数：

- `resolution_reasoning: reasoning`：The reasoning that notices the discrepancy, evaluates plausible interpretations, and adopts a resolution valid under those alternatives.
- `observation: observation`：The observed data whose content conflicts with labels, expectations, or assumed structure.

成立条件：

- The observation's content conflicts with labels, expected structure, or prior assumptions, and the reasoning explicitly notices the conflict.
- The reasoning considers more than one plausible interpretation of the discrepancy.
- The reasoning adopts a resolution or working assumption that stays valid under the plausible alternatives.

排除条件：

- The reasoning does not notice the discrepancy or takes the observation at face value.
- The discrepancy is noted but is irrelevant to the interpretation actually adopted.
- An interpretation is adopted without considering plausible alternatives, so the resolution is not conservative.

### SELECTS_OPTIMAL_CANDIDATE_BY_EXPLICIT_ORDERING

签名：`SELECTS_OPTIMAL_CANDIDATE_BY_EXPLICIT_ORDERING(selection_reasoning: reasoning)`

The reasoning enumerates or compares multiple candidate solutions, eliminates those that violate binding constraints, and selects from the survivors the candidate that is optimal under an explicit ordering or extremum criterion (such as earliest, cheapest, or smallest) that the reasoning states or applies.

参数：

- `selection_reasoning: reasoning`：The reasoning that compares candidates, eliminates constraint-violating ones, and selects an optimal survivor according to a stated ordering.

成立条件：

- Multiple candidate solutions are enumerated or compared.
- Candidates that violate one or more binding constraints are eliminated, either explicitly or by a stated filtering rule.
- An explicit ordering or extremum criterion is stated or applied to the surviving candidates.
- The selected candidate is the optimal survivor under that criterion.

排除条件：

- Only one candidate is considered, so no comparison or ordering is applied.
- The choice is arbitrary or rests on no stated ordering criterion.
- No candidate is excluded on constraint grounds.
- The stated ordering is not the basis of the final choice.

### PREPARES_VALIDATION_PROCEDURE

签名：`PREPARES_VALIDATION_PROCEDURE(validation_plan_reasoning: reasoning, procedure_creation_action: action)`

The reasoning specifies checks or expected conditions against which a produced solution is to be validated, and the action creates a reusable test or check procedure that embodies those checks so the solution can later be assessed against them.

参数：

- `validation_plan_reasoning: reasoning`：The reasoning that specifies the checks or expected conditions for validating the produced solution.
- `procedure_creation_action: action`：The action that creates the test or check procedure embodying those validation criteria.

成立条件：

- The reasoning enumerates concrete checks or expected conditions for validating the produced solution.
- The action creates a procedure (script, test, or checklist) that embodies those checks.
- The created procedure is intended to assess the produced solution against the stated requirements rather than to constitute the solution itself.

排除条件：

- The action creates or modifies the deliverable solution rather than a procedure for checking it.
- No concrete checks or expected conditions are specified before the procedure is created.
- The created procedure does not embody the stated validation checks.

### VERIFIES_INPUT_INTEGRITY

签名：`VERIFIES_INPUT_INTEGRITY(integrity_check_action: action, integrity_evidence_observation: observation, integrity_conclusion_reasoning: reasoning)`

Motivated by a requirement that input resources remain unmodified, an action retrieves metadata, checksums, or listings for those inputs, the observation supplies that integrity evidence, and the reasoning concludes from it that the inputs were not altered.

参数：

- `integrity_check_action: action`：The action that retrieves metadata, checksums, or listings for the input resources without modifying them.
- `integrity_evidence_observation: observation`：The observation containing the retrieved metadata, checksums, listings, or comparable evidence about input integrity.
- `integrity_conclusion_reasoning: reasoning`：The reasoning that concludes from the evidence that the input resources were not altered.

成立条件：

- A requirement or concern exists that the input resources must remain unmodified.
- The action retrieves metadata, checksums, listings, or comparable evidence about those inputs without modifying them.
- The observation supplies the retrieved integrity evidence.
- The reasoning concludes, on the basis of that evidence, that the inputs were not altered.

排除条件：

- No requirement or concern about input integrity is present.
- The action modifies the inputs or targets resources other than the inputs.
- The observation provides no evidence bearing on whether the inputs changed.
- The conclusion is asserted without reference to the evidence.
