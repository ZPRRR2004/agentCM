# 第 1 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：1–10
Prompt 版本：v0001
本批新增谓词：50
本批已有谓词修订：2
当前谓词总数：50

## 二、本批新增谓词

### PLANS_NEXT_ACTION

签名：`PLANS_NEXT_ACTION(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent has not yet performed.

参数：

- `reasoning: reasoning`：The reasoning node that states an intended future action or sequence.

成立条件：

- The reasoning explicitly identifies at least one intended future action or step.
- The intended action is presented as something still to be done rather than as already completed.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning states a conclusion, diagnosis, or observation summary without expressing future intent.

### IDENTIFIES_DEFECT_FROM_OBSERVATION

签名：`IDENTIFIES_DEFECT_FROM_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning uses identifiable content of an observation to identify a defect, error, or incompleteness in the artifact or state described by that observation.

参数：

- `reasoning: reasoning`：The reasoning node that identifies the defect, error, or gap.
- `observation: observation`：The observation whose content provides evidence of the defective or incomplete state.

成立条件：

- The observation contains identifiable evidence of an incomplete, erroneous, or otherwise defective state.
- The reasoning explicitly characterizes that state as a problem, gap, or defect requiring attention or correction.

排除条件：

- The reasoning merely repeats or describes the observation without identifying a defect.
- The observation does not contain evidence of a defect or gap.
- The reasoning asserts a defect that is not supported by identifiable observation content.

### FORMULATES_CORRECTIVE_SOLUTION

签名：`FORMULATES_CORRECTIVE_SOLUTION(reasoning: reasoning)`

The reasoning derives and specifies a concrete method, content, or set of steps intended to remedy an identified defect or gap.

参数：

- `reasoning: reasoning`：The reasoning node that derives and specifies the corrective method or steps.

成立条件：

- The reasoning refers to an identified defect, gap, or problematic state.
- The reasoning provides at least one concrete corrective step, replacement content, or method intended to address that defect.

排除条件：

- The reasoning only states that a fix is needed without specifying how to perform it.
- The reasoning only summarizes a correction that was already carried out.
- The reasoning only plans to investigate or gather information without formulating a corrective method.

### ACTION_IMPLEMENTS_PLANNED_STEP

签名：`ACTION_IMPLEMENTS_PLANNED_STEP(action: action, reasoning: reasoning)`

The action carries out a step that the reasoning explicitly specified as an intended future action or corrective step.

参数：

- `action: action`：The action performing the planned step.
- `reasoning: reasoning`：The reasoning node specifying the intended step, target, or corrective content.

成立条件：

- The reasoning specifies a future action, target, or corrective content.
- The action performs that specified step using a corresponding operation, target, or content.

排除条件：

- The action is unrelated to the reasoning's stated intent.
- The reasoning only describes an outcome or diagnosis without specifying an action.
- The action is an unplanned reaction that is not described in the reasoning.

### CHECKS_PREREQUISITE_AVAILABILITY

签名：`CHECKS_PREREQUISITE_AVAILABILITY(prerequisite_reasoning: reasoning, check_action: action, check_result: observation)`

The reasoning identifies a tool, resource, or environment capability on which a planned or contemplated action depends, a check action queries that prerequisite's availability, version, or readiness, and the observation reports its status.

参数：

- `prerequisite_reasoning: reasoning`：The reasoning node indicating that a planned or contemplated action depends on a required capability or resource, or that its availability must be verified.
- `check_action: action`：The action that queries availability, version, or readiness of the prerequisite.
- `check_result: observation`：The observation reporting the prerequisite's availability, version, or readiness.

成立条件：

- The reasoning links a planned or contemplated action to a prerequisite tool, resource, capability, or environment condition.
- The check action queries the availability, version, or readiness of that prerequisite rather than performing the planned work itself.
- The observation reports whether the prerequisite is available or ready.

排除条件：

- No planned or contemplated action depends on the checked prerequisite.
- The check action queries something unrelated to the stated dependency.
- The observation does not report availability, version, or readiness of the prerequisite.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(probe_action: action, assumption_reasoning: reasoning, probe_result: observation)`

A targeted action tests a specific uncertainty or hypothesis identified in reasoning, and the resulting observation provides interpretable evidence bearing on that uncertainty.

参数：

- `probe_action: action`：The targeted action that probes the uncertainty or hypothesis.
- `assumption_reasoning: reasoning`：The reasoning node identifying the hypothesis, property, or uncertainty being tested.
- `probe_result: observation`：The observation reporting a result relevant to the hypothesis or uncertainty.

成立条件：

- The reasoning identifies a specific uncertainty, hypothesis, or property to be checked.
- The probe action is directed at obtaining evidence about that specific uncertainty.
- The observation reports a result that can be interpreted as evidence about the uncertainty.

排除条件：

- The action is unrelated to the stated uncertainty or hypothesis.
- The observation does not address the uncertainty being tested.
- No identifiable uncertainty or hypothesis motivates the action.

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning explains a specific cause or mechanism responsible for a failure or error reported in an observation.

参数：

- `reasoning: reasoning`：The reasoning node explaining the cause of the failure.
- `observation: observation`：The observation reporting the error or unsuccessful outcome.

成立条件：

- The observation reports an error or unsuccessful outcome.
- The reasoning identifies a specific cause or mechanism responsible for that failure.

排除条件：

- The reasoning merely notes that a failure occurred.
- The reasoning proposes a retry without explaining the cause.
- The observation does not report a failure or error.

### CORRECTS_FAILED_ACTION_WITH_DIAGNOSIS

签名：`CORRECTS_FAILED_ACTION_WITH_DIAGNOSIS(corrected_action: action, diagnostic_reasoning: reasoning, failure_observation: observation)`

A subsequent action alters the approach, parameters, or resource of an earlier failing action in a way that follows from a diagnosed cause, aiming to overcome the observed failure.

参数：

- `corrected_action: action`：The subsequent action that changes the approach, parameters, or resource.
- `diagnostic_reasoning: reasoning`：The reasoning node diagnosing the cause and identifying the needed change.
- `failure_observation: observation`：The observation reporting the earlier failure or error.

成立条件：

- The failure observation reports an unsuccessful action or error.
- The reasoning diagnoses the cause of the failure and identifies a needed change.
- The corrected action implements the relevant change in parameter, resource, or approach.

排除条件：

- The subsequent action repeats the failed action without a relevant change.
- The action is not based on the diagnosed cause.
- The observation does not report a failure or error.

### CONFIRMS_EXPECTED_OUTCOME_FROM_OBSERVATION

签名：`CONFIRMS_EXPECTED_OUTCOME_FROM_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning interprets an observation as confirming that an expected condition, success criterion, or intended outcome has been achieved.

参数：

- `reasoning: reasoning`：The reasoning node interpreting the observation as confirmation.
- `observation: observation`：The observation providing evidence that matches the expected outcome.

成立条件：

- The reasoning states or implies an expected outcome or success criterion.
- The observation contains identifiable evidence matching that expectation.
- The reasoning explicitly treats the observation as confirmation that the expected outcome holds.

排除条件：

- The observation is used only as an input to further action rather than as confirmation.
- The reasoning merely predicts an outcome without checking it against an observation.
- The observation is ambiguous or unrelated to the expected condition.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning draws an explicit conclusion, diagnosis, or assessment that is supported by identifiable content of the observation.

参数：

- `reasoning: reasoning`：The reasoning node expressing the conclusion, diagnosis, or assessment.
- `observation: observation`：The observation supplying evidence for that conclusion.

成立条件：

- The reasoning states a conclusion, diagnosis, or assessment beyond merely restating the observation.
- The conclusion depends on specific identifiable content of the observation, such as presence or absence of items, status, version, or output.

排除条件：

- The reasoning repeats or describes the observation without inferring anything from it.
- The observation is unrelated to the conclusion or contains no information that supports it.
- The conclusion rests only on prior knowledge with no identifiable evidential link to the observation.

### IDENTIFIES_MISSING_PREREQUISITE

签名：`IDENTIFIES_MISSING_PREREQUISITE(reasoning: reasoning, observation: observation)`

The reasoning identifies a capability, component, account, resource, or configuration that the goal requires but that is absent or insufficient, using identifiable content of the observation as evidence of the gap.

参数：

- `reasoning: reasoning`：The reasoning node stating that something required for the goal is missing or inadequate.
- `observation: observation`：The observation providing evidence of the absence or insufficiency.

成立条件：

- The reasoning states that something needed for the task is missing, unavailable, or inadequate.
- The observation contains identifiable evidence of the absence or insufficiency, such as a failed lookup, empty listing, missing binary, or missing package.

排除条件：

- The reasoning merely notes a fact without linking it to a requirement of the goal.
- No requirement or gap is stated.
- The observation does not show absence or insufficiency of the required item.

### CONFIGURES_EVENT_TRIGGERED_AUTOMATION

签名：`CONFIGURES_EVENT_TRIGGERED_AUTOMATION(action: action)`

The action creates or updates a configuration artifact that associates a specified event with a downstream operation, so that later occurrences of the event automatically cause that operation without further manual invocation.

参数：

- `action: action`：The action node that writes or installs the automation configuration.

成立条件：

- The action writes or installs a hook, trigger, listener, job, or equivalent automation configuration.
- The configuration content associates a specified event or condition with a downstream operation to be performed automatically.

排除条件：

- The action performs a one-off operation with no persistent trigger.
- The action only documents a procedure for later manual execution.
- The configured artifact does not connect an event or condition to an automatic response.

### MITIGATES_ANTICIPATED_FAILURE

签名：`MITIGATES_ANTICIPATED_FAILURE(risk_reasoning: reasoning, mitigation_action: action, state_observation: observation)`

Reasoning identifies a foreseeable failure mode that could prevent the goal, an action applies a preventive measure addressing that failure mode before it occurs, and an observation provides evidence that the preventive measure is in place.

参数：

- `risk_reasoning: reasoning`：The reasoning node naming the anticipated failure mode or pitfall and its relevance to the goal.
- `mitigation_action: action`：The action node applying a preventive measure against that failure mode.
- `state_observation: observation`：The observation node showing evidence consistent with the preventive measure having been applied.

成立条件：

- The risk_reasoning names a specific failure mode or pitfall that could prevent the goal, rather than a vague risk.
- The mitigation_action changes configuration, permissions, or state in a way that prevents or reduces that failure mode before it occurs.
- The state_observation contains evidence consistent with the mitigation being applied.

排除条件：

- The reasoning only mentions a general risk without a corresponding preventive action.
- The action does not address the identified failure mode, or addresses it only after the failure occurred.
- The observation does not show the mitigated state.

### VALIDATES_CONFIGURATION_BEFORE_ACTIVATION

签名：`VALIDATES_CONFIGURATION_BEFORE_ACTIVATION(validation_reasoning: reasoning, validation_action: action, validation_observation: observation)`

A configuration artifact is checked for validity by a validation operation before the configured component is activated or relied upon, and the observed result confirms that the validation succeeded.

参数：

- `validation_reasoning: reasoning`：The reasoning node indicating that the configuration should be validated before activation.
- `validation_action: action`：The action node performing the configuration test or syntax check; activation of the component may occur in the same action or a subsequent one.
- `validation_observation: observation`：The observation node reporting the validation result.

成立条件：

- The validation_reasoning or the validation_action indicates a validation step is to be performed before the component is activated.
- The validation_action executes a configuration test, syntax check, or equivalent validity check on the artifact.
- The validation_observation reports a successful validation result, and activation follows that success.

排除条件：

- The component is activated without any preceding validation step.
- The validation fails or its result is not interpretable as success.
- Only a post-activation inspection is performed, with no pre-activation check.

### PREDICTS_RESIDUAL_ARTIFACT_INTERFERENCE

签名：`PREDICTS_RESIDUAL_ARTIFACT_INTERFERENCE(reasoning: reasoning)`

The reasoning predicts that state left behind by the agent's own activity (testing, probing, or configuration) will cause a later required operation, typically performed by the end user or an external checker, to fail or behave incorrectly, and uses that prediction as the reason to remove or reset that residual state before handoff.

参数：

- `reasoning: reasoning`：The agent text that identifies residual self-created state, predicts its adverse effect on a later operation, and motivates its removal.

成立条件：

- The reasoning identifies specific residual state produced by the agent's own activity, such as test commits, branches, keys, files, or running test artifacts.
- The reasoning predicts a concrete adverse consequence for a later operation, for example that a required commit will fail because nothing changed, that a push will report nothing to update, or that a check will observe pre-modified content.
- The reasoning treats that prediction as the justification for removing or resetting the identified state before handoff.

排除条件：

- The reasoning expresses only generic cleanliness or tidiness concerns without a predicted operational consequence.
- The predicted consequence concerns state the agent did not create, or state unrelated to its own testing or configuration.
- The reasoning plans cleanup solely because the state is no longer needed, with no predicted interference with a later operation.

### ATTRIBUTES_FAILURE_TO_TEST_HARNESS_ARTIFACT

签名：`ATTRIBUTES_FAILURE_TO_TEST_HARNESS_ARTIFACT(reasoning: reasoning, observation: observation)`

The reasoning classifies a failure observed during the agent's own verification procedure as an artifact of its test instrumentation or simulated conditions rather than as a defect in the delivered system, distinguishing the test-side conditions from the conditions the end user will actually use.

参数：

- `reasoning: reasoning`：The agent text that reinterprets the observed failure as a test-side artifact.
- `observation: observation`：The observation reporting the failure whose origin is being classified.

成立条件：

- The observation reports a failure that occurred during the agent's own verification or simulation procedure.
- The reasoning states that the failure originates in the agent's test setup, simulated credentials, ad hoc invocation, or missing test-side configuration rather than in the delivered system.
- The reasoning contrasts the test-side conditions with the conditions under which the end user or external checker will operate.

排除条件：

- The reasoning treats the failure as a genuine defect in the delivered configuration or state.
- The reasoning makes no distinction between test-side and user-side conditions.
- The reasoning reports the failure without interpreting where it originated.

### ENUMERATES_REQUIRED_END_STATE

签名：`ENUMERATES_REQUIRED_END_STATE(reasoning: reasoning)`

The reasoning enumerates multiple checkable conditions that the delivered environment must satisfy at handoff, decomposing the final state into individually verifiable invariants rather than listing actions to perform.

参数：

- `reasoning: reasoning`：The agent text listing the conditions the final environment must satisfy.

成立条件：

- The reasoning lists multiple distinct conditions the final environment must satisfy, such as services running, repository empty, keys removed, and host entries present.
- The listed conditions are phrased as verifiable properties of the resulting state rather than as steps to execute.

排除条件：

- The reasoning describes a sequence of actions to execute without stating the resulting state conditions.
- The reasoning states only a single observation about the current state, with no enumeration of required end-state properties.

### IMPLEMENTS_GUARDED_RECOVERY

签名：`IMPLEMENTS_GUARDED_RECOVERY(resilience_reasoning: reasoning, creation_action: action, creation_result: observation)`

The reasoning establishes that a required capability must survive interruption or restart, and an action creates a repeatable, guard-checked, non-failing mechanism that restores that capability only when it is absent, with an observation confirming creation of the mechanism.

参数：

- `resilience_reasoning: reasoning`：The agent text identifying the need for the required capability to be restored after restart or interruption.
- `creation_action: action`：The action creating the guarded recovery mechanism.
- `creation_result: observation`：The observation confirming that the mechanism was created and made usable.

成立条件：

- The reasoning frames the mechanism as a safety net keeping a required capability available across restarts, rather than as a one-time start of that capability.
- The mechanism as created includes a presence check so an already-running capability is not duplicated or restarted.
- The mechanism is specified to be silent and to terminate successfully so it cannot break the invoking session.
- The observation reports successful creation of the mechanism.

排除条件：

- The mechanism unconditionally starts the capability regardless of whether it is already running.
- The mechanism can fail or emit output that affects the calling context.
- The intent is a one-time activation of the capability with no restart or resilience rationale.

### RECOVERS_CHECK_WITH_ALTERNATIVE_METHOD

签名：`RECOVERS_CHECK_WITH_ALTERNATIVE_METHOD(inconclusive_result: observation, method_diagnosis: reasoning, alternative_action: action)`

An executed check yields an empty or otherwise unusable result, the reasoning attributes that unusability to a concrete limitation of the check's method or tooling rather than to the inspected state, and a follow-up action retrieves the intended information using a materially different technique.

参数：

- `inconclusive_result: observation`：The observation reporting the empty, missing, or otherwise unusable result of the original check.
- `method_diagnosis: reasoning`：The reasoning explaining which property of the check's method or tooling caused the unusable result.
- `alternative_action: action`：The follow-up action that retrieves the intended information through a different technique.

成立条件：

- The observation reports that the original check produced no interpretable information, such as empty output, absent entries, or an unparseable result.
- The reasoning identifies a concrete limitation of that check's method or tooling (for example unsupported syntax, symlink handling, or wrong format) as the cause of the unusable result.
- The alternative action targets the same information and uses a materially different technique or invocation than the original check.

排除条件：

- The reasoning attributes the unusable result to an actual defect or genuine absence in the inspected system.
- The follow-up action repeats the same method or only cosmetic variations of it.
- No reasoning distinguishes a tooling artifact from a genuine negative finding.

### DISMISSES_ANOMALY_AS_BENIGN

签名：`DISMISSES_ANOMALY_AS_BENIGN(interpretive_reasoning: reasoning, anomalous_observation: observation)`

The observation contains an unexpected artifact that deviates from the expected clean state, and the reasoning explains it with an identified benign origin while judging that it does not impair the required behavior.

参数：

- `interpretive_reasoning: reasoning`：The reasoning that explains the anomaly's origin and judges whether it is harmful.
- `anomalous_observation: observation`：The observation containing the unusual entry, state, or residual artifact being explained.

成立条件：

- The observation contains content that deviates from the expected clean or normal state, such as non-listening socket states, defunct processes, or residual entries.
- The reasoning names a plausible cause or origin for that content instead of merely noting it.
- The reasoning explicitly judges the anomaly as harmless with respect to the required behavior, supported by or consistent with independent evidence that the required behavior still holds.

排除条件：

- The reasoning treats the anomalous content as a fault that must be repaired.
- The reasoning ignores the anomalous content instead of explaining it.
- The anomaly is dismissed without any stated cause, or while contradicting evidence shows the required behavior is impaired.

### REPRODUCES_STIPULATED_WORKFLOW

签名：`REPRODUCES_STIPULATED_WORKFLOW(validation_reasoning: reasoning, replay_action: action)`

The action replays the exact procedure stipulated by the task or requester, mirroring its steps instead of substituting a proxy check, so that the stipulated procedure itself is validated.

参数：

- `validation_reasoning: reasoning`：The reasoning stating that the stipulated procedure itself is being replayed for validation.
- `replay_action: action`：The action whose operations reproduce the stipulated steps.

成立条件：

- The reasoning states that the procedure the requester is expected to run is itself being replayed in order to validate it.
- The action contains the same operations, in the same sequence or spirit, as the stipulated procedure rather than an indirect substitute such as a status query or configuration inspection.

排除条件：

- The action performs an equivalent but different check that does not reproduce the stipulated sequence.
- The reasoning does not connect the action to the stipulated procedure.
- The action merely inspects state or configuration without exercising the user-facing workflow.

### SELECTS_SUBSTITUTE_APPROACH_UNDER_CONSTRAINT

签名：`SELECTS_SUBSTITUTE_APPROACH_UNDER_CONSTRAINT(constraint_reasoning: reasoning, substitute_action: action)`

The reasoning identifies an unavailable facility or imposed restriction, weighs how the same effect can still be achieved, and justifies the alternative approach that the associated action then implements.

参数：

- `constraint_reasoning: reasoning`：The reasoning identifying the limitation and justifying the chosen alternative.
- `substitute_action: action`：The action implementing the justified alternative approach.

成立条件：

- The reasoning explicitly identifies an unavailable tool, capability, or imposed constraint that blocks the obvious approach.
- The reasoning considers alternatives and explains why the selected alternative achieves the same effect despite that constraint.
- The associated action implements the approach the reasoning justifies.

排除条件：

- The reasoning describes the action without any stated constraint motivating the choice.
- The action does not correspond to the approach the reasoning justifies.
- No alternatives are weighed; the action is merely the only obvious single step.

### AUDITS_MULTIPLE_INVARIANTS

签名：`AUDITS_MULTIPLE_INVARIANTS(checklist_reasoning: reasoning, audit_action: action, audit_result: observation)`

The reasoning enumerates several independent conditions that the environment must satisfy, a single action evaluates those conditions together, and the observation reports outcomes attributable to the individual conditions.

参数：

- `checklist_reasoning: reasoning`：The reasoning listing the independent conditions the audit must cover.
- `audit_action: action`：The action evaluating the listed conditions together in one invocation.
- `audit_result: observation`：The observation reporting per-condition results of the audit.

成立条件：

- The reasoning enumerates at least two independent conditions or invariants to be verified.
- The audit action probes multiple of those enumerated conditions within a single invocation.
- The observation reports results that can be attributed to individual conditions rather than a single undifferentiated status.

排除条件：

- Only a single condition is checked.
- The observation aggregates outcomes so that individual conditions cannot be distinguished.
- The action does not actually probe the enumerated conditions.

### RESETS_TO_PRISTINE_STATE_FOR_HANDOFF

签名：`RESETS_TO_PRISTINE_STATE_FOR_HANDOFF(handoff_reasoning: reasoning, reset_action: action)`

The reasoning explains that the environment should be returned to its initial, empty condition so that subsequent use by the recipient behaves without conflicts, and the action removes or empties the artifacts produced during setup and validation while leaving the required configuration intact.

参数：

- `handoff_reasoning: reasoning`：The reasoning justifying restoring the initial state before handing the environment over.
- `reset_action: action`：The action deleting, emptying, or reverting the artifacts created during the work.

成立条件：

- The reasoning states that the environment is being returned to its starting or empty condition for the benefit of subsequent use.
- The reset action removes or empties artifacts created during setup or validation.
- The reset action preserves the configured infrastructure that the recipient needs.

排除条件：

- Artifacts are deleted for ordinary tidiness without a stated handoff rationale.
- The action reverts required configuration rather than only produced data.
- The reasoning does not address the state in which the environment is left.

### FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS

签名：`FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS(reasoning: reasoning)`

The reasoning converts informally stated requirements or preferences into explicit, mechanically checkable conditions — such as bounds, admissible ranges, or excluded intervals — against which candidate solutions can be accepted or rejected.

参数：

- `reasoning: reasoning`：The reasoning text that restates the stated requirements as testable admissibility conditions or admissible ranges.

成立条件：

- The reasoning derives at least one explicit admissibility condition from the stated requirements rather than restating them verbatim.
- The derived condition is precise enough to accept or reject a candidate solution.

排除条件：

- The reasoning only repeats the original requirement wording without converting it into a testable condition.
- The reasoning merely lists preferences or observations without deriving any admissibility condition.

### SELECTS_CANDIDATE_BY_CONSTRAINT_ELIMINATION

签名：`SELECTS_CANDIDATE_BY_CONSTRAINT_ELIMINATION(reasoning: reasoning)`

The reasoning evaluates multiple candidate options, explicitly rejects those that violate stated hard requirements, and identifies a surviving candidate as the selected outcome, optionally using soft preferences only to break ties among survivors.

参数：

- `reasoning: reasoning`：The reasoning text that enumerates candidate options, rejects violating ones, and names the selected option.

成立条件：

- The reasoning considers more than one candidate option.
- At least one candidate is rejected with an explicit reason tied to a hard requirement.
- A surviving candidate is identified as the selected outcome.

排除条件：

- The reasoning asserts a chosen option without evaluating any alternative.
- The reasoning enumerates candidates but never reaches a selection.
- Rejections are based on arbitrary or unstated grounds rather than on stated requirements.

### DERIVES_CONSTRAINT_INPUTS_FROM_OBSERVED_RECORDS

签名：`DERIVES_CONSTRAINT_INPUTS_FROM_OBSERVED_RECORDS(reasoning: reasoning, observation: observation)`

The reasoning extracts specific values from the content of an observation and transforms them into derived quantities, such as occupied intervals, ranges, totals, or parsed records, that serve as inputs constraining the subsequent solution or decision.

参数：

- `reasoning: reasoning`：The reasoning text that extracts values from observed records and computes derived quantities from them.
- `observation: observation`：The observation whose content supplies the underlying records or values being transformed.

成立条件：

- The reasoning cites or transforms specific content present in the observation.
- The derived quantities are used as inputs to the subsequent constraint evaluation or decision rather than merely described.

排除条件：

- The reasoning discusses the observation only in general terms without extracting concrete values.
- The observation's content is not used in the derived quantities.
- The reasoning only restates the observation's content without computing anything from it.

### DETECTS_OBSERVED_DATA_INCONSISTENCY

签名：`DETECTS_OBSERVED_DATA_INCONSISTENCY(reasoning: reasoning, observation: observation)`

The reasoning identifies an explicit discrepancy between the content of an observation and what its labeling, structure, or surrounding context led the agent to expect, and states that discrepancy as a finding.

参数：

- `reasoning: reasoning`：The reasoning text that names the mismatch between observed content and the expectation.
- `observation: observation`：The observation whose content contains the unexpected or inconsistent element.

成立条件：

- The reasoning states what was expected and what was actually observed.
- The inconsistency is attributable to identifiable content in the observation.

排除条件：

- The reasoning only summarizes the observation without comparing it to an expectation.
- The claimed mismatch is between two reasoning statements rather than traced to the observation's content.
- No expectation about the observation's content is articulated.

### CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION

签名：`CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION(reasoning: reasoning, inspection_action: action, inspection_result: observation)`

The reasoning states the goal of confirming that protected or read-only inputs remain unaltered, a non-mutating inspection action is performed for that purpose, and the resulting observation reports state information bearing on whether those inputs are unchanged.

参数：

- `reasoning: reasoning`：The reasoning text expressing the intention to confirm that the inputs were not modified.
- `inspection_action: action`：The non-mutating action (listing, checksum, or read) applied to the input artifacts.
- `inspection_result: observation`：The observation reporting metadata, checksums, or contents relevant to the inputs' integrity.

成立条件：

- The reasoning states that preserving or confirming the unmodified state of the inputs is the purpose of the check.
- The inspection action does not write to or otherwise alter the inspected inputs.
- The observation reports metadata, checksums, or contents that bear on whether the inputs are unchanged.

排除条件：

- The action modifies the inspected inputs.
- The inspection serves solution production rather than confirming input integrity.
- No observation reports the inspection's outcome.

### DECOMPOSES_TASK_INTO_SUBGOALS

签名：`DECOMPOSES_TASK_INTO_SUBGOALS(reasoning: reasoning)`

The reasoning breaks an overall task into two or more distinct subgoals, questions, or procedural steps that stand in an ordering or dependency relationship and can guide subsequent execution.

参数：

- `reasoning: reasoning`：The reasoning node that decomposes the overall task into subgoals or procedural steps.

成立条件：

- The reasoning identifies at least two distinct subgoals, questions, or procedural steps.
- The subgoals or steps are presented with an ordering, dependency, or execution relationship rather than as an unrelated collection.
- The decomposition is derived from the stated task and is specific enough to guide execution.

排除条件：

- The reasoning identifies only a single intended action or subgoal.
- The reasoning merely restates the overall task without dividing it into executable parts.
- The reasoning lists unrelated facts or observations that are not presented as parts of the task.

### OPERATIONALIZES_UNDERSPECIFIED_REQUIREMENT

签名：`OPERATIONALIZES_UNDERSPECIFIED_REQUIREMENT(reasoning: reasoning)`

The reasoning recognizes an ambiguous or underspecified aspect of a requirement and commits to a concrete, executable interpretation — such as which fields to process, which filter condition to apply, which metric to compute, or which tool to use — that can guide the procedure.

参数：

- `reasoning: reasoning`：The reasoning node that resolves an ambiguity or underspecification into an operational interpretation.

成立条件：

- The reasoning identifies an ambiguity, an alternative reading, or an underspecified aspect of the requirement.
- The reasoning commits to a concrete operational definition or procedure rather than leaving the ambiguity open.
- The selected interpretation is specific enough to determine which data, condition, metric, or tool will be used.

排除条件：

- The requirement is already fully specified and the reasoning only restates it.
- The reasoning notes an ambiguity but does not resolve it into an operational definition.
- The reasoning supplies procedural detail that is not tied to interpreting the requirement.

### REMEDIES_MISSING_CAPABILITY

签名：`REMEDIES_MISSING_CAPABILITY(gap_reasoning: reasoning, provisioning_action: action, confirmation_observation: observation)`

The reasoning identifies a specific dependency, tool, library, or capability that the task requires but that is absent; a provisioning action installs or otherwise supplies that identified capability; and an observation confirms that the capability has become available.

参数：

- `gap_reasoning: reasoning`：The reasoning node identifying the dependency, tool, or capability that is missing and required for the task.
- `provisioning_action: action`：The action that installs, supplies, or otherwise provisions the identified capability.
- `confirmation_observation: observation`：The observation reporting that the capability has been installed or is now available.

成立条件：

- The reasoning identifies a specific dependency, tool, or capability as missing and required for the task.
- The provisioning action is directed at supplying or installing that identified capability rather than at performing the task work itself.
- The observation reports successful installation or confirmed availability of the capability.

排除条件：

- No specific missing dependency, tool, or capability is identified.
- The action does not provision the identified capability.
- The observation does not confirm availability, or the provisioning outcome is left unknown.

### TRANSLATES_SCHEMA_EVIDENCE_INTO_PROCESSING_PROCEDURE

签名：`TRANSLATES_SCHEMA_EVIDENCE_INTO_PROCESSING_PROCEDURE(schema_observation: observation, interpretation_reasoning: reasoning, implementation_action: action)`

An observation supplies structural, schema, field-list, format, or documented layout information about a resource; the reasoning uses that structural information to determine which fields, parameters, or operations the task requires; and an action creates or executes a procedure that implements that determination.

参数：

- `schema_observation: observation`：The observation containing schema, field, format, or documented layout information about the resource.
- `interpretation_reasoning: reasoning`：The reasoning that maps the task requirements onto the fields, parameters, or operations indicated by the structural evidence.
- `implementation_action: action`：The action creating or executing a procedure that implements the determined interpretation.

成立条件：

- The observation contains structural, schema, field-list, format, or documented layout information relevant to the resource.
- The reasoning explicitly uses that structural information to determine which fields, parameters, or operations the task requires.
- The action creates or executes a procedure that operationalizes the interpretation rather than merely retrieving or inspecting data.

排除条件：

- The observation contains only values or results without structural or schema information.
- The reasoning does not reference the structural or field information when determining the procedure.
- The action retrieves or inspects data but does not implement a procedure derived from the structural evidence.

### SURVEYS_ENVIRONMENT_STATE_FOR_PLANNING

签名：`SURVEYS_ENVIRONMENT_STATE_FOR_PLANNING(planning_reasoning: reasoning, exploratory_action: action, state_observation: observation)`

The reasoning indicates that some environment or resource state is unknown, unchecked, or relevant to planning; a reconnaissance action inspects, lists, or queries that state; and the resulting observation reports state information that can inform subsequent decisions.

参数：

- `planning_reasoning: reasoning`：The reasoning node indicating that environment or resource state is unknown, must be checked, or is relevant to planning.
- `exploratory_action: action`：The action performing an inspection, listing, or query of the environment or resource state.
- `state_observation: observation`：The observation reporting the inspected environment or resource state.

成立条件：

- The reasoning indicates that some environment or resource state is unknown, must be checked, or is relevant to planning.
- The exploratory action inspects, lists, or queries that environment or resource state rather than performing a substantive transformation or final computation.
- The observation reports state information relevant to subsequent planning or decisions.

排除条件：

- The action performs a substantive transformation or final computation rather than an inspection of state.
- The reasoning already has the relevant state and expresses no reconnaissance need.
- The observation is unrelated to the environment or resource state being surveyed.

### CORROBORATES_RESULT_WITH_INDEPENDENT_PATH

签名：`CORROBORATES_RESULT_WITH_INDEPENDENT_PATH(baseline_result: observation, validation_action: action, validation_result: observation)`

A previously obtained result is recomputed through a materially different data-access or implementation path in order to check for agreement, and the second observation reproduces the same value for the same quantity.

参数：

- `baseline_result: observation`：The observation reporting the first computed value produced by the original implementation path.
- `validation_action: action`：The action recomputing the same quantity through a materially different data-access or implementation path.
- `validation_result: observation`：The observation reporting the recomputed value obtained from the alternative path.

成立条件：

- The baseline observation reports a specific computed value.
- The validation action uses a different loading, access, or implementation path than the one that produced the baseline value (for example a different library, interface, or format reader for the same underlying data).
- The validation observation reports the same value for the same quantity as the baseline, so the independent paths agree.

排除条件：

- The second run repeats the identical code or access path, so agreement is not informative.
- The recomputed quantity, scope, or selection differs from the baseline.
- The two observations report different values, or no baseline value exists.
- The second observation only inspects the persisted output rather than recomputing the quantity.

### CONFIRMS_PERSISTED_OUTPUT_MATCHES_COMPUTED_VALUE

签名：`CONFIRMS_PERSISTED_OUTPUT_MATCHES_COMPUTED_VALUE(computed_result: observation, inspection_action: action, artifact_observation: observation)`

An action inspects the persisted output artifact, and its observation shows artifact content identical to a value the agent previously computed, confirming that the stored output faithfully reflects the computed result.

参数：

- `computed_result: observation`：The observation reporting the value produced by the computation.
- `inspection_action: action`：The action that reads, lists, or otherwise inspects the persisted output artifact.
- `artifact_observation: observation`：The observation showing the content of the persisted output artifact.

成立条件：

- The computed result observation reports a specific value produced by the agent's computation.
- The inspection action targets the file or artifact to which that value was written.
- The artifact observation shows content whose value is identical to the reported computed value, including any required formatting constraints.

排除条件：

- The artifact content is missing, empty, truncated, or differs from the computed value.
- The inspection action does not read or list the output artifact.
- No previously computed value exists to compare against.
- Agreement is only asserted in reasoning but is not visible in the artifact observation.

### CONCLUDES_WITH_FINAL_ANSWER

签名：`CONCLUDES_WITH_FINAL_ANSWER(conclusion_reasoning: reasoning)`

The reasoning presents the definitive final result of the task, connects it to the supporting evidence chain (and, where applicable, to the produced output artifact), and asserts that the task is complete.

参数：

- `conclusion_reasoning: reasoning`：The agent text presenting the final result together with its supporting justification and a completion claim.

成立条件：

- The reasoning presents a specific final value or result as the answer to the task.
- The reasoning links that result to identifiable supporting evidence, such as prior observations, and to any produced output artifact when one was required.
- The reasoning explicitly states that the task is complete or finished.

排除条件：

- The reasoning is intermediate, exploratory, or tentative about the result.
- No final value or result is stated.
- The reasoning only describes steps or plans without asserting completion.
- The stated result is presented only as a candidate still subject to further verification.

### ENUMERATES_COMPETING_EXPLANATIONS

签名：`ENUMERATES_COMPETING_EXPLANATIONS(reasoning: reasoning)`

The reasoning lays out two or more alternative explanations for the same observed situation, treating them as rival candidates whose truth is still to be determined before a course of action is chosen.

参数：

- `reasoning: reasoning`：The reasoning node enumerating the alternative explanations for the observed situation.

成立条件：

- At least two distinct candidate explanations are stated for the same observed condition.
- The alternatives are presented as competing, still-undetermined possibilities rather than as settled findings.

排除条件：

- Only a single explanation is offered.
- The enumerated items are steps of a plan, candidate solutions, or facts about the state rather than rival explanations for why the state is as observed.
- One explanation is already asserted as established, so no genuine competition between alternatives remains.

### ELIMINATES_EXPLANATION_WITH_CONTRARY_EVIDENCE

签名：`ELIMINATES_EXPLANATION_WITH_CONTRARY_EVIDENCE(reasoning: reasoning, observation: observation)`

The reasoning discards a candidate explanation for an observed situation because identifiable content of an observation contradicts a condition that the explanation requires.

参数：

- `reasoning: reasoning`：The reasoning node rejecting the candidate explanation.
- `observation: observation`：The observation whose content contradicts the rejected explanation.

成立条件：

- The reasoning names or clearly refers to a candidate explanation it discards.
- The reasoning cites identifiable observation content that conflicts with what that explanation would require, such as an empty listing contradicting a stash hypothesis or a clean status contradicting an uncommitted-changes hypothesis.

排除条件：

- The reasoning narrows possibilities without stating what rules a candidate out.
- The observation is compatible with the discarded explanation or unrelated to it.
- What is discarded is a candidate solution or artifact rather than an explanation for the observed situation.

### SELECTS_TARGET_AMONG_CANDIDATES

签名：`SELECTS_TARGET_AMONG_CANDIDATES(reasoning: reasoning, observation: observation)`

The reasoning identifies which of several comparable candidate items is the one relevant to the task, justifying the choice with discriminating attributes visible in an observation rather than by position, recency, or surface similarity.

参数：

- `reasoning: reasoning`：The reasoning node comparing the candidates and identifying the relevant one.
- `observation: observation`：The observation exposing the discriminating attributes of the candidates.

成立条件：

- At least two comparable candidate items are distinguished in the reasoning.
- The selection is justified by at least one discriminating attribute visible in the observation, such as provenance, authorship, timestamp, or creation context.
- The reasoning concludes that one candidate is the item relevant to the task.

排除条件：

- Only one candidate is considered, so no discrimination is needed.
- A candidate is chosen by position, recency, or guess without cited discriminating evidence.
- The cited discriminating attribute is not actually present in the observation.

### PREDICTS_OUTCOME_OF_PLANNED_OPERATION

签名：`PREDICTS_OUTCOME_OF_PLANNED_OPERATION(reasoning: reasoning, observation: observation)`

The reasoning forecasts a specific consequence of an operation it has not yet performed, deriving that forecast from identifiable state evidence reported in an observation.

参数：

- `reasoning: reasoning`：The reasoning node naming the planned operation and stating the predicted consequence.
- `observation: observation`：The observation supplying the state evidence on which the forecast rests.

成立条件：

- The reasoning names an operation that is planned but not yet performed.
- A specific expected consequence of that operation is stated, such as an anticipated conflict, failure, or produced change.
- The forecast is tied to identifiable state evidence in the observation.

排除条件：

- The reasoning describes an outcome that has already been observed.
- The forecast is speculation not connected to identifiable state evidence.
- No specific consequence is predicted.
- The observation content cited is unrelated to the predicted consequence.

### DIAGNOSES_ROOT_CAUSE

签名：`DIAGNOSES_ROOT_CAUSE(reasoning: reasoning)`

The reasoning reconstructs a causal account of how an observed state came to be, specifying the preceding events or actions responsible for it rather than merely restating what the state is.

参数：

- `reasoning: reasoning`：The reasoning node presenting the causal reconstruction of the observed state.

成立条件：

- The reasoning specifies one or more preceding events or actions, in sequence, as the cause of the observed condition.
- The account explains why the current state has the observed properties, not merely what those properties are.

排除条件：

- The reasoning only restates the reported problem or the observed state.
- The reasoning lists possible causes without committing to a causal account.
- The reasoning merely paraphrases observed output without identifying the preceding events that produced it.

### ESTABLISHES_CONFLICT_RESOLUTION_PRECEDENCE

签名：`ESTABLISHES_CONFLICT_RESOLUTION_PRECEDENCE(reasoning: reasoning, observation: observation)`

Given an observation showing that two versions of the same artifact conflict, the reasoning decides which version prevails and justifies that choice with a stated precedence rationale rather than an arbitrary pick.

参数：

- `reasoning: reasoning`：The reasoning node choosing the prevailing version and stating the precedence rationale.
- `observation: observation`：The observation exhibiting the conflicting versions of the artifact.

成立条件：

- The observation presents two conflicting alternatives for the same artifact.
- The reasoning selects one alternative as the resulting outcome.
- The reasoning states a rationale for why that alternative supersedes the other, such as which change is newer or which reflects the current situation.

排除条件：

- The reasoning only describes the conflict without selecting a side.
- A side is selected without any stated justification, or purely by position or convenience.
- The observation does not actually show conflicting alternatives for the same artifact.

### PLANS_POST_ACTION_VERIFICATION

签名：`PLANS_POST_ACTION_VERIFICATION(reasoning: reasoning)`

The reasoning explicitly plans one or more checks to be performed after an action in order to determine whether the action produced the required outcome or final state.

参数：

- `reasoning: reasoning`：The reasoning text specifying the future verification checks and their purpose.

成立条件：

- The reasoning refers to future verification or checking steps.
- The checks are directed at confirming the outcome or final state of a completed or planned action, rather than at initial exploration.
- At least one check criterion or target state is identifiable.

排除条件：

- The reasoning only describes exploratory inspection before any relevant action.
- The reasoning only reports checks already completed without planning future verification.
- The reasoning states a general next step without a validation purpose.

### RESOLVES_OBSERVED_CONFLICT_BY_SELECTING_VERSION

签名：`RESOLVES_OBSERVED_CONFLICT_BY_SELECTING_VERSION(conflict_observation: observation, resolution_reasoning: reasoning, resolution_action: action)`

An observation identifies competing alternative contents in a target artifact; the reasoning selects one alternative with an explicit justification; the action applies the selected alternative to resolve the conflict.

参数：

- `conflict_observation: observation`：The observation showing incompatible alternatives, conflict markers, or otherwise competing versions of the target content.
- `resolution_reasoning: reasoning`：The reasoning that selects one competing version and gives a justification for that selection.
- `resolution_action: action`：The action that applies the selected version or otherwise carries out the conflict resolution.

成立条件：

- The observation contains identifiable conflicting or competing content alternatives.
- The reasoning states which alternative is adopted and gives an identifiable semantic reason such as precedence, correctness, or supersession.
- The action implements that selected alternative, for example by adopting, staging, or committing that version.

排除条件：

- The observation does not contain an identifiable conflict or competing versions.
- The reasoning only notes the presence of a conflict without selecting a version.
- The action is unrelated to the selected version or applies a different resolution.
- No justification for the selection is provided.

### DERIVES_EXACTNESS_CONSTRAINT_FROM_MEASUREMENT

签名：`DERIVES_EXACTNESS_CONSTRAINT_FROM_MEASUREMENT(measurement_observation: observation, reasoning: reasoning)`

The reasoning extracts a precise measurable or formatting property from an observation and adopts preservation of that property as a requirement for a subsequent action or acceptance check.

参数：

- `measurement_observation: observation`：The observation reporting an exact quantitative or formatting property such as byte count, hash, whitespace pattern, or exact text layout.
- `reasoning: reasoning`：The reasoning that refers to the precise property as a requirement to be matched or preserved.

成立条件：

- The observation provides a precise measurable, byte-level, or formatting property.
- The reasoning explicitly refers to that property as something that must be matched or preserved.
- The property is used as a constraint on a subsequent action or as an acceptance criterion.

排除条件：

- The observation provides only qualitative or approximate information.
- The reasoning does not impose preservation or matching of the measured property.
- The measured property is mentioned but not used as a requirement or acceptance criterion.

### ACTION_RESULT_CONFIRMS_INTENDED_EFFECT

签名：`ACTION_RESULT_CONFIRMS_INTENDED_EFFECT(action: action, result_observation: observation)`

The observation reports a resulting state that confirms the action achieved its intended effect, rather than merely indicating that the action was invoked or completed.

参数：

- `action: action`：The action whose intended effect is being assessed.
- `result_observation: observation`：The observation reporting the resulting state after the action.

成立条件：

- The observation contains an outcome state that matches the action's intended effect.
- No error or contradictory state undermines that claimed effect.
- The effect is inferred from the reported state, not merely from an acknowledgment that the command was executed.

排除条件：

- The observation only shows that the action was invoked or completed without evidence of its effect.
- The observation reports an error, failure, or incomplete result for the intended effect.
- The observation is unrelated to the action's intended effect.

### LOCATES_TARGET_WITHIN_OBSERVED_STRUCTURE

签名：`LOCATES_TARGET_WITHIN_OBSERVED_STRUCTURE(reasoning: reasoning, observation: observation)`

The reasoning identifies a specific element within a structure, history, or set of records described by an observation as the location, container, or source of a target of interest.

参数：

- `reasoning: reasoning`：The reasoning node pinpointing a specific locus of the target within the observed structure.
- `observation: observation`：The observation describing the structure, history, or set of records being searched.

成立条件：

- The observation describes a structure, history, or set of records with identifiable individual elements.
- The reasoning points to at least one specific element within that observed structure as containing, retaining, or being associated with the target of interest.

排除条件：

- The reasoning only summarizes the observed structure without singling out any element.
- The reasoning states a target value without relating it to a location or record visible in the observation.
- The observation does not contain the structure or records being localized.

### PERSISTS_RECOVERED_VALUE_TO_OUTPUT

签名：`PERSISTS_RECOVERED_VALUE_TO_OUTPUT(action: action, reasoning: reasoning)`

An action writes a specific value that reasoning has identified as recovered or extracted information into the output artifact designated for it, so that the discovered value is preserved outside the search process.

参数：

- `action: action`：The action that writes or creates the designated output artifact.
- `reasoning: reasoning`：The reasoning identifying the recovered value and the output destination where it must be persisted.

成立条件：

- The reasoning identifies a specific value as recovered or extracted and indicates the output location where it should be persisted.
- The action writes that identified value to the indicated output artifact.

排除条件：

- The action writes unrelated, placeholder, or unverified content.
- The reasoning does not identify a recovered value or an output destination.
- The action only reads or inspects information without persisting it.

### APPLIES_REMEDIATION_TO_IDENTIFIED_ARTIFACT

签名：`APPLIES_REMEDIATION_TO_IDENTIFIED_ARTIFACT(action: action, reasoning: reasoning)`

An action performs a removal or elimination operation directed at an unwanted artifact, record, or retention mechanism that the reasoning has identified as the thing to be cleaned up.

参数：

- `action: action`：The action executing the cleanup or removal operation.
- `reasoning: reasoning`：The reasoning identifying the unwanted artifact, record, or retention mechanism and the removal strategy.

成立条件：

- The reasoning identifies a specific unwanted artifact, record, or mechanism that retains it.
- The reasoning indicates a strategy for removing or eliminating that target.
- The action executes an operation directed at that removal rather than at exploration or verification.

排除条件：

- The action is exploratory, diagnostic, or unrelated maintenance.
- The reasoning does not identify an unwanted artifact or retention mechanism.
- The action only checks whether removal is needed without performing removal.
- The action removes state merely for tidiness, with no identified unwanted target.

## 三、本批已有谓词修订

### DIAGNOSES_FAILURE_CAUSE → DIAGNOSES_FAILURE_CAUSE

Window：xhigh__configure-git-webserver__window_0002

修订前：

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning explains a specific cause or mechanism responsible for a failure or error reported in an observation.

参数：

- `reasoning: reasoning`：The reasoning node explaining the cause of the failure.
- `observation: observation`：The observation reporting the error or unsuccessful outcome.

成立条件：

- The observation reports an error or unsuccessful outcome.
- The reasoning identifies a specific cause or mechanism responsible for that failure.

排除条件：

- The reasoning merely notes that a failure occurred.
- The reasoning proposes a retry without explaining the cause.
- The observation does not report a failure or error.

修订后：

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning assigns a specific causal mechanism to a failure or error reported in an observation, explaining how the failure arose rather than merely restating the error text.

参数：

- `reasoning: reasoning`：The reasoning node explaining the cause or mechanism of the failure.
- `observation: observation`：The observation reporting the error or unsuccessful outcome.

成立条件：

- The observation reports an error, non-zero exit status, or otherwise unsuccessful outcome.
- The reasoning identifies a specific cause or mechanism responsible for that failure, going beyond the literal error message.
- The stated cause is consistent with the facts reported in the observation.

排除条件：

- The reasoning merely notes that a failure occurred.
- The reasoning proposes a retry without explaining the cause.
- The reasoning only repeats or paraphrases the error message without explaining it.
- The stated cause contradicts the observation's reported facts.
- The observation does not report a failure or error.

### PLANS_NEXT_ACTION → PLANS_NEXT_ACTION

Window：xhigh__count-dataset-tokens__window_0001

修订前：

### PLANS_NEXT_ACTION

签名：`PLANS_NEXT_ACTION(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent has not yet performed.

参数：

- `reasoning: reasoning`：The reasoning node that states an intended future action or sequence.

成立条件：

- The reasoning explicitly identifies at least one intended future action or step.
- The intended action is presented as something still to be done rather than as already completed.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning states a conclusion, diagnosis, or observation summary without expressing future intent.

修订后：

### PLANS_NEXT_ACTION

签名：`PLANS_NEXT_ACTION(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent has not yet performed.

参数：

- `reasoning: reasoning`：The reasoning node that states an intended future action or sequence.

成立条件：

- The reasoning explicitly identifies at least one intended future action or step.
- The intended action is presented as something still to be done rather than as already completed.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning states a conclusion, diagnosis, or observation summary without expressing future intent.
- The reasoning states only a general goal or desired result without identifying any intended action or step.

## 四、当前完整 Registry

### PLANS_NEXT_ACTION

签名：`PLANS_NEXT_ACTION(reasoning: reasoning)`

The reasoning explicitly expresses an intended future action or sequence of actions that the agent has not yet performed.

参数：

- `reasoning: reasoning`：The reasoning node that states an intended future action or sequence.

成立条件：

- The reasoning explicitly identifies at least one intended future action or step.
- The intended action is presented as something still to be done rather than as already completed.

排除条件：

- The reasoning only reports or summarizes actions already completed.
- The reasoning states a conclusion, diagnosis, or observation summary without expressing future intent.
- The reasoning states only a general goal or desired result without identifying any intended action or step.

### IDENTIFIES_DEFECT_FROM_OBSERVATION

签名：`IDENTIFIES_DEFECT_FROM_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning uses identifiable content of an observation to identify a defect, error, or incompleteness in the artifact or state described by that observation.

参数：

- `reasoning: reasoning`：The reasoning node that identifies the defect, error, or gap.
- `observation: observation`：The observation whose content provides evidence of the defective or incomplete state.

成立条件：

- The observation contains identifiable evidence of an incomplete, erroneous, or otherwise defective state.
- The reasoning explicitly characterizes that state as a problem, gap, or defect requiring attention or correction.

排除条件：

- The reasoning merely repeats or describes the observation without identifying a defect.
- The observation does not contain evidence of a defect or gap.
- The reasoning asserts a defect that is not supported by identifiable observation content.

### FORMULATES_CORRECTIVE_SOLUTION

签名：`FORMULATES_CORRECTIVE_SOLUTION(reasoning: reasoning)`

The reasoning derives and specifies a concrete method, content, or set of steps intended to remedy an identified defect or gap.

参数：

- `reasoning: reasoning`：The reasoning node that derives and specifies the corrective method or steps.

成立条件：

- The reasoning refers to an identified defect, gap, or problematic state.
- The reasoning provides at least one concrete corrective step, replacement content, or method intended to address that defect.

排除条件：

- The reasoning only states that a fix is needed without specifying how to perform it.
- The reasoning only summarizes a correction that was already carried out.
- The reasoning only plans to investigate or gather information without formulating a corrective method.

### ACTION_IMPLEMENTS_PLANNED_STEP

签名：`ACTION_IMPLEMENTS_PLANNED_STEP(action: action, reasoning: reasoning)`

The action carries out a step that the reasoning explicitly specified as an intended future action or corrective step.

参数：

- `action: action`：The action performing the planned step.
- `reasoning: reasoning`：The reasoning node specifying the intended step, target, or corrective content.

成立条件：

- The reasoning specifies a future action, target, or corrective content.
- The action performs that specified step using a corresponding operation, target, or content.

排除条件：

- The action is unrelated to the reasoning's stated intent.
- The reasoning only describes an outcome or diagnosis without specifying an action.
- The action is an unplanned reaction that is not described in the reasoning.

### CHECKS_PREREQUISITE_AVAILABILITY

签名：`CHECKS_PREREQUISITE_AVAILABILITY(prerequisite_reasoning: reasoning, check_action: action, check_result: observation)`

The reasoning identifies a tool, resource, or environment capability on which a planned or contemplated action depends, a check action queries that prerequisite's availability, version, or readiness, and the observation reports its status.

参数：

- `prerequisite_reasoning: reasoning`：The reasoning node indicating that a planned or contemplated action depends on a required capability or resource, or that its availability must be verified.
- `check_action: action`：The action that queries availability, version, or readiness of the prerequisite.
- `check_result: observation`：The observation reporting the prerequisite's availability, version, or readiness.

成立条件：

- The reasoning links a planned or contemplated action to a prerequisite tool, resource, capability, or environment condition.
- The check action queries the availability, version, or readiness of that prerequisite rather than performing the planned work itself.
- The observation reports whether the prerequisite is available or ready.

排除条件：

- No planned or contemplated action depends on the checked prerequisite.
- The check action queries something unrelated to the stated dependency.
- The observation does not report availability, version, or readiness of the prerequisite.

### TESTS_ASSUMPTION_WITH_PROBE

签名：`TESTS_ASSUMPTION_WITH_PROBE(probe_action: action, assumption_reasoning: reasoning, probe_result: observation)`

A targeted action tests a specific uncertainty or hypothesis identified in reasoning, and the resulting observation provides interpretable evidence bearing on that uncertainty.

参数：

- `probe_action: action`：The targeted action that probes the uncertainty or hypothesis.
- `assumption_reasoning: reasoning`：The reasoning node identifying the hypothesis, property, or uncertainty being tested.
- `probe_result: observation`：The observation reporting a result relevant to the hypothesis or uncertainty.

成立条件：

- The reasoning identifies a specific uncertainty, hypothesis, or property to be checked.
- The probe action is directed at obtaining evidence about that specific uncertainty.
- The observation reports a result that can be interpreted as evidence about the uncertainty.

排除条件：

- The action is unrelated to the stated uncertainty or hypothesis.
- The observation does not address the uncertainty being tested.
- No identifiable uncertainty or hypothesis motivates the action.

### DIAGNOSES_FAILURE_CAUSE

签名：`DIAGNOSES_FAILURE_CAUSE(reasoning: reasoning, observation: observation)`

The reasoning assigns a specific causal mechanism to a failure or error reported in an observation, explaining how the failure arose rather than merely restating the error text.

参数：

- `reasoning: reasoning`：The reasoning node explaining the cause or mechanism of the failure.
- `observation: observation`：The observation reporting the error or unsuccessful outcome.

成立条件：

- The observation reports an error, non-zero exit status, or otherwise unsuccessful outcome.
- The reasoning identifies a specific cause or mechanism responsible for that failure, going beyond the literal error message.
- The stated cause is consistent with the facts reported in the observation.

排除条件：

- The reasoning merely notes that a failure occurred.
- The reasoning proposes a retry without explaining the cause.
- The reasoning only repeats or paraphrases the error message without explaining it.
- The stated cause contradicts the observation's reported facts.
- The observation does not report a failure or error.

### CORRECTS_FAILED_ACTION_WITH_DIAGNOSIS

签名：`CORRECTS_FAILED_ACTION_WITH_DIAGNOSIS(corrected_action: action, diagnostic_reasoning: reasoning, failure_observation: observation)`

A subsequent action alters the approach, parameters, or resource of an earlier failing action in a way that follows from a diagnosed cause, aiming to overcome the observed failure.

参数：

- `corrected_action: action`：The subsequent action that changes the approach, parameters, or resource.
- `diagnostic_reasoning: reasoning`：The reasoning node diagnosing the cause and identifying the needed change.
- `failure_observation: observation`：The observation reporting the earlier failure or error.

成立条件：

- The failure observation reports an unsuccessful action or error.
- The reasoning diagnoses the cause of the failure and identifies a needed change.
- The corrected action implements the relevant change in parameter, resource, or approach.

排除条件：

- The subsequent action repeats the failed action without a relevant change.
- The action is not based on the diagnosed cause.
- The observation does not report a failure or error.

### CONFIRMS_EXPECTED_OUTCOME_FROM_OBSERVATION

签名：`CONFIRMS_EXPECTED_OUTCOME_FROM_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning interprets an observation as confirming that an expected condition, success criterion, or intended outcome has been achieved.

参数：

- `reasoning: reasoning`：The reasoning node interpreting the observation as confirmation.
- `observation: observation`：The observation providing evidence that matches the expected outcome.

成立条件：

- The reasoning states or implies an expected outcome or success criterion.
- The observation contains identifiable evidence matching that expectation.
- The reasoning explicitly treats the observation as confirmation that the expected outcome holds.

排除条件：

- The observation is used only as an input to further action rather than as confirmation.
- The reasoning merely predicts an outcome without checking it against an observation.
- The observation is ambiguous or unrelated to the expected condition.

### GROUNDS_CONCLUSION_IN_OBSERVATION

签名：`GROUNDS_CONCLUSION_IN_OBSERVATION(reasoning: reasoning, observation: observation)`

The reasoning draws an explicit conclusion, diagnosis, or assessment that is supported by identifiable content of the observation.

参数：

- `reasoning: reasoning`：The reasoning node expressing the conclusion, diagnosis, or assessment.
- `observation: observation`：The observation supplying evidence for that conclusion.

成立条件：

- The reasoning states a conclusion, diagnosis, or assessment beyond merely restating the observation.
- The conclusion depends on specific identifiable content of the observation, such as presence or absence of items, status, version, or output.

排除条件：

- The reasoning repeats or describes the observation without inferring anything from it.
- The observation is unrelated to the conclusion or contains no information that supports it.
- The conclusion rests only on prior knowledge with no identifiable evidential link to the observation.

### IDENTIFIES_MISSING_PREREQUISITE

签名：`IDENTIFIES_MISSING_PREREQUISITE(reasoning: reasoning, observation: observation)`

The reasoning identifies a capability, component, account, resource, or configuration that the goal requires but that is absent or insufficient, using identifiable content of the observation as evidence of the gap.

参数：

- `reasoning: reasoning`：The reasoning node stating that something required for the goal is missing or inadequate.
- `observation: observation`：The observation providing evidence of the absence or insufficiency.

成立条件：

- The reasoning states that something needed for the task is missing, unavailable, or inadequate.
- The observation contains identifiable evidence of the absence or insufficiency, such as a failed lookup, empty listing, missing binary, or missing package.

排除条件：

- The reasoning merely notes a fact without linking it to a requirement of the goal.
- No requirement or gap is stated.
- The observation does not show absence or insufficiency of the required item.

### CONFIGURES_EVENT_TRIGGERED_AUTOMATION

签名：`CONFIGURES_EVENT_TRIGGERED_AUTOMATION(action: action)`

The action creates or updates a configuration artifact that associates a specified event with a downstream operation, so that later occurrences of the event automatically cause that operation without further manual invocation.

参数：

- `action: action`：The action node that writes or installs the automation configuration.

成立条件：

- The action writes or installs a hook, trigger, listener, job, or equivalent automation configuration.
- The configuration content associates a specified event or condition with a downstream operation to be performed automatically.

排除条件：

- The action performs a one-off operation with no persistent trigger.
- The action only documents a procedure for later manual execution.
- The configured artifact does not connect an event or condition to an automatic response.

### MITIGATES_ANTICIPATED_FAILURE

签名：`MITIGATES_ANTICIPATED_FAILURE(risk_reasoning: reasoning, mitigation_action: action, state_observation: observation)`

Reasoning identifies a foreseeable failure mode that could prevent the goal, an action applies a preventive measure addressing that failure mode before it occurs, and an observation provides evidence that the preventive measure is in place.

参数：

- `risk_reasoning: reasoning`：The reasoning node naming the anticipated failure mode or pitfall and its relevance to the goal.
- `mitigation_action: action`：The action node applying a preventive measure against that failure mode.
- `state_observation: observation`：The observation node showing evidence consistent with the preventive measure having been applied.

成立条件：

- The risk_reasoning names a specific failure mode or pitfall that could prevent the goal, rather than a vague risk.
- The mitigation_action changes configuration, permissions, or state in a way that prevents or reduces that failure mode before it occurs.
- The state_observation contains evidence consistent with the mitigation being applied.

排除条件：

- The reasoning only mentions a general risk without a corresponding preventive action.
- The action does not address the identified failure mode, or addresses it only after the failure occurred.
- The observation does not show the mitigated state.

### VALIDATES_CONFIGURATION_BEFORE_ACTIVATION

签名：`VALIDATES_CONFIGURATION_BEFORE_ACTIVATION(validation_reasoning: reasoning, validation_action: action, validation_observation: observation)`

A configuration artifact is checked for validity by a validation operation before the configured component is activated or relied upon, and the observed result confirms that the validation succeeded.

参数：

- `validation_reasoning: reasoning`：The reasoning node indicating that the configuration should be validated before activation.
- `validation_action: action`：The action node performing the configuration test or syntax check; activation of the component may occur in the same action or a subsequent one.
- `validation_observation: observation`：The observation node reporting the validation result.

成立条件：

- The validation_reasoning or the validation_action indicates a validation step is to be performed before the component is activated.
- The validation_action executes a configuration test, syntax check, or equivalent validity check on the artifact.
- The validation_observation reports a successful validation result, and activation follows that success.

排除条件：

- The component is activated without any preceding validation step.
- The validation fails or its result is not interpretable as success.
- Only a post-activation inspection is performed, with no pre-activation check.

### PREDICTS_RESIDUAL_ARTIFACT_INTERFERENCE

签名：`PREDICTS_RESIDUAL_ARTIFACT_INTERFERENCE(reasoning: reasoning)`

The reasoning predicts that state left behind by the agent's own activity (testing, probing, or configuration) will cause a later required operation, typically performed by the end user or an external checker, to fail or behave incorrectly, and uses that prediction as the reason to remove or reset that residual state before handoff.

参数：

- `reasoning: reasoning`：The agent text that identifies residual self-created state, predicts its adverse effect on a later operation, and motivates its removal.

成立条件：

- The reasoning identifies specific residual state produced by the agent's own activity, such as test commits, branches, keys, files, or running test artifacts.
- The reasoning predicts a concrete adverse consequence for a later operation, for example that a required commit will fail because nothing changed, that a push will report nothing to update, or that a check will observe pre-modified content.
- The reasoning treats that prediction as the justification for removing or resetting the identified state before handoff.

排除条件：

- The reasoning expresses only generic cleanliness or tidiness concerns without a predicted operational consequence.
- The predicted consequence concerns state the agent did not create, or state unrelated to its own testing or configuration.
- The reasoning plans cleanup solely because the state is no longer needed, with no predicted interference with a later operation.

### ATTRIBUTES_FAILURE_TO_TEST_HARNESS_ARTIFACT

签名：`ATTRIBUTES_FAILURE_TO_TEST_HARNESS_ARTIFACT(reasoning: reasoning, observation: observation)`

The reasoning classifies a failure observed during the agent's own verification procedure as an artifact of its test instrumentation or simulated conditions rather than as a defect in the delivered system, distinguishing the test-side conditions from the conditions the end user will actually use.

参数：

- `reasoning: reasoning`：The agent text that reinterprets the observed failure as a test-side artifact.
- `observation: observation`：The observation reporting the failure whose origin is being classified.

成立条件：

- The observation reports a failure that occurred during the agent's own verification or simulation procedure.
- The reasoning states that the failure originates in the agent's test setup, simulated credentials, ad hoc invocation, or missing test-side configuration rather than in the delivered system.
- The reasoning contrasts the test-side conditions with the conditions under which the end user or external checker will operate.

排除条件：

- The reasoning treats the failure as a genuine defect in the delivered configuration or state.
- The reasoning makes no distinction between test-side and user-side conditions.
- The reasoning reports the failure without interpreting where it originated.

### ENUMERATES_REQUIRED_END_STATE

签名：`ENUMERATES_REQUIRED_END_STATE(reasoning: reasoning)`

The reasoning enumerates multiple checkable conditions that the delivered environment must satisfy at handoff, decomposing the final state into individually verifiable invariants rather than listing actions to perform.

参数：

- `reasoning: reasoning`：The agent text listing the conditions the final environment must satisfy.

成立条件：

- The reasoning lists multiple distinct conditions the final environment must satisfy, such as services running, repository empty, keys removed, and host entries present.
- The listed conditions are phrased as verifiable properties of the resulting state rather than as steps to execute.

排除条件：

- The reasoning describes a sequence of actions to execute without stating the resulting state conditions.
- The reasoning states only a single observation about the current state, with no enumeration of required end-state properties.

### IMPLEMENTS_GUARDED_RECOVERY

签名：`IMPLEMENTS_GUARDED_RECOVERY(resilience_reasoning: reasoning, creation_action: action, creation_result: observation)`

The reasoning establishes that a required capability must survive interruption or restart, and an action creates a repeatable, guard-checked, non-failing mechanism that restores that capability only when it is absent, with an observation confirming creation of the mechanism.

参数：

- `resilience_reasoning: reasoning`：The agent text identifying the need for the required capability to be restored after restart or interruption.
- `creation_action: action`：The action creating the guarded recovery mechanism.
- `creation_result: observation`：The observation confirming that the mechanism was created and made usable.

成立条件：

- The reasoning frames the mechanism as a safety net keeping a required capability available across restarts, rather than as a one-time start of that capability.
- The mechanism as created includes a presence check so an already-running capability is not duplicated or restarted.
- The mechanism is specified to be silent and to terminate successfully so it cannot break the invoking session.
- The observation reports successful creation of the mechanism.

排除条件：

- The mechanism unconditionally starts the capability regardless of whether it is already running.
- The mechanism can fail or emit output that affects the calling context.
- The intent is a one-time activation of the capability with no restart or resilience rationale.

### RECOVERS_CHECK_WITH_ALTERNATIVE_METHOD

签名：`RECOVERS_CHECK_WITH_ALTERNATIVE_METHOD(inconclusive_result: observation, method_diagnosis: reasoning, alternative_action: action)`

An executed check yields an empty or otherwise unusable result, the reasoning attributes that unusability to a concrete limitation of the check's method or tooling rather than to the inspected state, and a follow-up action retrieves the intended information using a materially different technique.

参数：

- `inconclusive_result: observation`：The observation reporting the empty, missing, or otherwise unusable result of the original check.
- `method_diagnosis: reasoning`：The reasoning explaining which property of the check's method or tooling caused the unusable result.
- `alternative_action: action`：The follow-up action that retrieves the intended information through a different technique.

成立条件：

- The observation reports that the original check produced no interpretable information, such as empty output, absent entries, or an unparseable result.
- The reasoning identifies a concrete limitation of that check's method or tooling (for example unsupported syntax, symlink handling, or wrong format) as the cause of the unusable result.
- The alternative action targets the same information and uses a materially different technique or invocation than the original check.

排除条件：

- The reasoning attributes the unusable result to an actual defect or genuine absence in the inspected system.
- The follow-up action repeats the same method or only cosmetic variations of it.
- No reasoning distinguishes a tooling artifact from a genuine negative finding.

### DISMISSES_ANOMALY_AS_BENIGN

签名：`DISMISSES_ANOMALY_AS_BENIGN(interpretive_reasoning: reasoning, anomalous_observation: observation)`

The observation contains an unexpected artifact that deviates from the expected clean state, and the reasoning explains it with an identified benign origin while judging that it does not impair the required behavior.

参数：

- `interpretive_reasoning: reasoning`：The reasoning that explains the anomaly's origin and judges whether it is harmful.
- `anomalous_observation: observation`：The observation containing the unusual entry, state, or residual artifact being explained.

成立条件：

- The observation contains content that deviates from the expected clean or normal state, such as non-listening socket states, defunct processes, or residual entries.
- The reasoning names a plausible cause or origin for that content instead of merely noting it.
- The reasoning explicitly judges the anomaly as harmless with respect to the required behavior, supported by or consistent with independent evidence that the required behavior still holds.

排除条件：

- The reasoning treats the anomalous content as a fault that must be repaired.
- The reasoning ignores the anomalous content instead of explaining it.
- The anomaly is dismissed without any stated cause, or while contradicting evidence shows the required behavior is impaired.

### REPRODUCES_STIPULATED_WORKFLOW

签名：`REPRODUCES_STIPULATED_WORKFLOW(validation_reasoning: reasoning, replay_action: action)`

The action replays the exact procedure stipulated by the task or requester, mirroring its steps instead of substituting a proxy check, so that the stipulated procedure itself is validated.

参数：

- `validation_reasoning: reasoning`：The reasoning stating that the stipulated procedure itself is being replayed for validation.
- `replay_action: action`：The action whose operations reproduce the stipulated steps.

成立条件：

- The reasoning states that the procedure the requester is expected to run is itself being replayed in order to validate it.
- The action contains the same operations, in the same sequence or spirit, as the stipulated procedure rather than an indirect substitute such as a status query or configuration inspection.

排除条件：

- The action performs an equivalent but different check that does not reproduce the stipulated sequence.
- The reasoning does not connect the action to the stipulated procedure.
- The action merely inspects state or configuration without exercising the user-facing workflow.

### SELECTS_SUBSTITUTE_APPROACH_UNDER_CONSTRAINT

签名：`SELECTS_SUBSTITUTE_APPROACH_UNDER_CONSTRAINT(constraint_reasoning: reasoning, substitute_action: action)`

The reasoning identifies an unavailable facility or imposed restriction, weighs how the same effect can still be achieved, and justifies the alternative approach that the associated action then implements.

参数：

- `constraint_reasoning: reasoning`：The reasoning identifying the limitation and justifying the chosen alternative.
- `substitute_action: action`：The action implementing the justified alternative approach.

成立条件：

- The reasoning explicitly identifies an unavailable tool, capability, or imposed constraint that blocks the obvious approach.
- The reasoning considers alternatives and explains why the selected alternative achieves the same effect despite that constraint.
- The associated action implements the approach the reasoning justifies.

排除条件：

- The reasoning describes the action without any stated constraint motivating the choice.
- The action does not correspond to the approach the reasoning justifies.
- No alternatives are weighed; the action is merely the only obvious single step.

### AUDITS_MULTIPLE_INVARIANTS

签名：`AUDITS_MULTIPLE_INVARIANTS(checklist_reasoning: reasoning, audit_action: action, audit_result: observation)`

The reasoning enumerates several independent conditions that the environment must satisfy, a single action evaluates those conditions together, and the observation reports outcomes attributable to the individual conditions.

参数：

- `checklist_reasoning: reasoning`：The reasoning listing the independent conditions the audit must cover.
- `audit_action: action`：The action evaluating the listed conditions together in one invocation.
- `audit_result: observation`：The observation reporting per-condition results of the audit.

成立条件：

- The reasoning enumerates at least two independent conditions or invariants to be verified.
- The audit action probes multiple of those enumerated conditions within a single invocation.
- The observation reports results that can be attributed to individual conditions rather than a single undifferentiated status.

排除条件：

- Only a single condition is checked.
- The observation aggregates outcomes so that individual conditions cannot be distinguished.
- The action does not actually probe the enumerated conditions.

### RESETS_TO_PRISTINE_STATE_FOR_HANDOFF

签名：`RESETS_TO_PRISTINE_STATE_FOR_HANDOFF(handoff_reasoning: reasoning, reset_action: action)`

The reasoning explains that the environment should be returned to its initial, empty condition so that subsequent use by the recipient behaves without conflicts, and the action removes or empties the artifacts produced during setup and validation while leaving the required configuration intact.

参数：

- `handoff_reasoning: reasoning`：The reasoning justifying restoring the initial state before handing the environment over.
- `reset_action: action`：The action deleting, emptying, or reverting the artifacts created during the work.

成立条件：

- The reasoning states that the environment is being returned to its starting or empty condition for the benefit of subsequent use.
- The reset action removes or empties artifacts created during setup or validation.
- The reset action preserves the configured infrastructure that the recipient needs.

排除条件：

- Artifacts are deleted for ordinary tidiness without a stated handoff rationale.
- The action reverts required configuration rather than only produced data.
- The reasoning does not address the state in which the environment is left.

### FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS

签名：`FORMALIZES_CONSTRAINTS_AS_CHECKABLE_CONDITIONS(reasoning: reasoning)`

The reasoning converts informally stated requirements or preferences into explicit, mechanically checkable conditions — such as bounds, admissible ranges, or excluded intervals — against which candidate solutions can be accepted or rejected.

参数：

- `reasoning: reasoning`：The reasoning text that restates the stated requirements as testable admissibility conditions or admissible ranges.

成立条件：

- The reasoning derives at least one explicit admissibility condition from the stated requirements rather than restating them verbatim.
- The derived condition is precise enough to accept or reject a candidate solution.

排除条件：

- The reasoning only repeats the original requirement wording without converting it into a testable condition.
- The reasoning merely lists preferences or observations without deriving any admissibility condition.

### SELECTS_CANDIDATE_BY_CONSTRAINT_ELIMINATION

签名：`SELECTS_CANDIDATE_BY_CONSTRAINT_ELIMINATION(reasoning: reasoning)`

The reasoning evaluates multiple candidate options, explicitly rejects those that violate stated hard requirements, and identifies a surviving candidate as the selected outcome, optionally using soft preferences only to break ties among survivors.

参数：

- `reasoning: reasoning`：The reasoning text that enumerates candidate options, rejects violating ones, and names the selected option.

成立条件：

- The reasoning considers more than one candidate option.
- At least one candidate is rejected with an explicit reason tied to a hard requirement.
- A surviving candidate is identified as the selected outcome.

排除条件：

- The reasoning asserts a chosen option without evaluating any alternative.
- The reasoning enumerates candidates but never reaches a selection.
- Rejections are based on arbitrary or unstated grounds rather than on stated requirements.

### DERIVES_CONSTRAINT_INPUTS_FROM_OBSERVED_RECORDS

签名：`DERIVES_CONSTRAINT_INPUTS_FROM_OBSERVED_RECORDS(reasoning: reasoning, observation: observation)`

The reasoning extracts specific values from the content of an observation and transforms them into derived quantities, such as occupied intervals, ranges, totals, or parsed records, that serve as inputs constraining the subsequent solution or decision.

参数：

- `reasoning: reasoning`：The reasoning text that extracts values from observed records and computes derived quantities from them.
- `observation: observation`：The observation whose content supplies the underlying records or values being transformed.

成立条件：

- The reasoning cites or transforms specific content present in the observation.
- The derived quantities are used as inputs to the subsequent constraint evaluation or decision rather than merely described.

排除条件：

- The reasoning discusses the observation only in general terms without extracting concrete values.
- The observation's content is not used in the derived quantities.
- The reasoning only restates the observation's content without computing anything from it.

### DETECTS_OBSERVED_DATA_INCONSISTENCY

签名：`DETECTS_OBSERVED_DATA_INCONSISTENCY(reasoning: reasoning, observation: observation)`

The reasoning identifies an explicit discrepancy between the content of an observation and what its labeling, structure, or surrounding context led the agent to expect, and states that discrepancy as a finding.

参数：

- `reasoning: reasoning`：The reasoning text that names the mismatch between observed content and the expectation.
- `observation: observation`：The observation whose content contains the unexpected or inconsistent element.

成立条件：

- The reasoning states what was expected and what was actually observed.
- The inconsistency is attributable to identifiable content in the observation.

排除条件：

- The reasoning only summarizes the observation without comparing it to an expectation.
- The claimed mismatch is between two reasoning statements rather than traced to the observation's content.
- No expectation about the observation's content is articulated.

### CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION

签名：`CHECKS_INPUT_INTEGRITY_WITHOUT_MODIFICATION(reasoning: reasoning, inspection_action: action, inspection_result: observation)`

The reasoning states the goal of confirming that protected or read-only inputs remain unaltered, a non-mutating inspection action is performed for that purpose, and the resulting observation reports state information bearing on whether those inputs are unchanged.

参数：

- `reasoning: reasoning`：The reasoning text expressing the intention to confirm that the inputs were not modified.
- `inspection_action: action`：The non-mutating action (listing, checksum, or read) applied to the input artifacts.
- `inspection_result: observation`：The observation reporting metadata, checksums, or contents relevant to the inputs' integrity.

成立条件：

- The reasoning states that preserving or confirming the unmodified state of the inputs is the purpose of the check.
- The inspection action does not write to or otherwise alter the inspected inputs.
- The observation reports metadata, checksums, or contents that bear on whether the inputs are unchanged.

排除条件：

- The action modifies the inspected inputs.
- The inspection serves solution production rather than confirming input integrity.
- No observation reports the inspection's outcome.

### DECOMPOSES_TASK_INTO_SUBGOALS

签名：`DECOMPOSES_TASK_INTO_SUBGOALS(reasoning: reasoning)`

The reasoning breaks an overall task into two or more distinct subgoals, questions, or procedural steps that stand in an ordering or dependency relationship and can guide subsequent execution.

参数：

- `reasoning: reasoning`：The reasoning node that decomposes the overall task into subgoals or procedural steps.

成立条件：

- The reasoning identifies at least two distinct subgoals, questions, or procedural steps.
- The subgoals or steps are presented with an ordering, dependency, or execution relationship rather than as an unrelated collection.
- The decomposition is derived from the stated task and is specific enough to guide execution.

排除条件：

- The reasoning identifies only a single intended action or subgoal.
- The reasoning merely restates the overall task without dividing it into executable parts.
- The reasoning lists unrelated facts or observations that are not presented as parts of the task.

### OPERATIONALIZES_UNDERSPECIFIED_REQUIREMENT

签名：`OPERATIONALIZES_UNDERSPECIFIED_REQUIREMENT(reasoning: reasoning)`

The reasoning recognizes an ambiguous or underspecified aspect of a requirement and commits to a concrete, executable interpretation — such as which fields to process, which filter condition to apply, which metric to compute, or which tool to use — that can guide the procedure.

参数：

- `reasoning: reasoning`：The reasoning node that resolves an ambiguity or underspecification into an operational interpretation.

成立条件：

- The reasoning identifies an ambiguity, an alternative reading, or an underspecified aspect of the requirement.
- The reasoning commits to a concrete operational definition or procedure rather than leaving the ambiguity open.
- The selected interpretation is specific enough to determine which data, condition, metric, or tool will be used.

排除条件：

- The requirement is already fully specified and the reasoning only restates it.
- The reasoning notes an ambiguity but does not resolve it into an operational definition.
- The reasoning supplies procedural detail that is not tied to interpreting the requirement.

### REMEDIES_MISSING_CAPABILITY

签名：`REMEDIES_MISSING_CAPABILITY(gap_reasoning: reasoning, provisioning_action: action, confirmation_observation: observation)`

The reasoning identifies a specific dependency, tool, library, or capability that the task requires but that is absent; a provisioning action installs or otherwise supplies that identified capability; and an observation confirms that the capability has become available.

参数：

- `gap_reasoning: reasoning`：The reasoning node identifying the dependency, tool, or capability that is missing and required for the task.
- `provisioning_action: action`：The action that installs, supplies, or otherwise provisions the identified capability.
- `confirmation_observation: observation`：The observation reporting that the capability has been installed or is now available.

成立条件：

- The reasoning identifies a specific dependency, tool, or capability as missing and required for the task.
- The provisioning action is directed at supplying or installing that identified capability rather than at performing the task work itself.
- The observation reports successful installation or confirmed availability of the capability.

排除条件：

- No specific missing dependency, tool, or capability is identified.
- The action does not provision the identified capability.
- The observation does not confirm availability, or the provisioning outcome is left unknown.

### TRANSLATES_SCHEMA_EVIDENCE_INTO_PROCESSING_PROCEDURE

签名：`TRANSLATES_SCHEMA_EVIDENCE_INTO_PROCESSING_PROCEDURE(schema_observation: observation, interpretation_reasoning: reasoning, implementation_action: action)`

An observation supplies structural, schema, field-list, format, or documented layout information about a resource; the reasoning uses that structural information to determine which fields, parameters, or operations the task requires; and an action creates or executes a procedure that implements that determination.

参数：

- `schema_observation: observation`：The observation containing schema, field, format, or documented layout information about the resource.
- `interpretation_reasoning: reasoning`：The reasoning that maps the task requirements onto the fields, parameters, or operations indicated by the structural evidence.
- `implementation_action: action`：The action creating or executing a procedure that implements the determined interpretation.

成立条件：

- The observation contains structural, schema, field-list, format, or documented layout information relevant to the resource.
- The reasoning explicitly uses that structural information to determine which fields, parameters, or operations the task requires.
- The action creates or executes a procedure that operationalizes the interpretation rather than merely retrieving or inspecting data.

排除条件：

- The observation contains only values or results without structural or schema information.
- The reasoning does not reference the structural or field information when determining the procedure.
- The action retrieves or inspects data but does not implement a procedure derived from the structural evidence.

### SURVEYS_ENVIRONMENT_STATE_FOR_PLANNING

签名：`SURVEYS_ENVIRONMENT_STATE_FOR_PLANNING(planning_reasoning: reasoning, exploratory_action: action, state_observation: observation)`

The reasoning indicates that some environment or resource state is unknown, unchecked, or relevant to planning; a reconnaissance action inspects, lists, or queries that state; and the resulting observation reports state information that can inform subsequent decisions.

参数：

- `planning_reasoning: reasoning`：The reasoning node indicating that environment or resource state is unknown, must be checked, or is relevant to planning.
- `exploratory_action: action`：The action performing an inspection, listing, or query of the environment or resource state.
- `state_observation: observation`：The observation reporting the inspected environment or resource state.

成立条件：

- The reasoning indicates that some environment or resource state is unknown, must be checked, or is relevant to planning.
- The exploratory action inspects, lists, or queries that environment or resource state rather than performing a substantive transformation or final computation.
- The observation reports state information relevant to subsequent planning or decisions.

排除条件：

- The action performs a substantive transformation or final computation rather than an inspection of state.
- The reasoning already has the relevant state and expresses no reconnaissance need.
- The observation is unrelated to the environment or resource state being surveyed.

### CORROBORATES_RESULT_WITH_INDEPENDENT_PATH

签名：`CORROBORATES_RESULT_WITH_INDEPENDENT_PATH(baseline_result: observation, validation_action: action, validation_result: observation)`

A previously obtained result is recomputed through a materially different data-access or implementation path in order to check for agreement, and the second observation reproduces the same value for the same quantity.

参数：

- `baseline_result: observation`：The observation reporting the first computed value produced by the original implementation path.
- `validation_action: action`：The action recomputing the same quantity through a materially different data-access or implementation path.
- `validation_result: observation`：The observation reporting the recomputed value obtained from the alternative path.

成立条件：

- The baseline observation reports a specific computed value.
- The validation action uses a different loading, access, or implementation path than the one that produced the baseline value (for example a different library, interface, or format reader for the same underlying data).
- The validation observation reports the same value for the same quantity as the baseline, so the independent paths agree.

排除条件：

- The second run repeats the identical code or access path, so agreement is not informative.
- The recomputed quantity, scope, or selection differs from the baseline.
- The two observations report different values, or no baseline value exists.
- The second observation only inspects the persisted output rather than recomputing the quantity.

### CONFIRMS_PERSISTED_OUTPUT_MATCHES_COMPUTED_VALUE

签名：`CONFIRMS_PERSISTED_OUTPUT_MATCHES_COMPUTED_VALUE(computed_result: observation, inspection_action: action, artifact_observation: observation)`

An action inspects the persisted output artifact, and its observation shows artifact content identical to a value the agent previously computed, confirming that the stored output faithfully reflects the computed result.

参数：

- `computed_result: observation`：The observation reporting the value produced by the computation.
- `inspection_action: action`：The action that reads, lists, or otherwise inspects the persisted output artifact.
- `artifact_observation: observation`：The observation showing the content of the persisted output artifact.

成立条件：

- The computed result observation reports a specific value produced by the agent's computation.
- The inspection action targets the file or artifact to which that value was written.
- The artifact observation shows content whose value is identical to the reported computed value, including any required formatting constraints.

排除条件：

- The artifact content is missing, empty, truncated, or differs from the computed value.
- The inspection action does not read or list the output artifact.
- No previously computed value exists to compare against.
- Agreement is only asserted in reasoning but is not visible in the artifact observation.

### CONCLUDES_WITH_FINAL_ANSWER

签名：`CONCLUDES_WITH_FINAL_ANSWER(conclusion_reasoning: reasoning)`

The reasoning presents the definitive final result of the task, connects it to the supporting evidence chain (and, where applicable, to the produced output artifact), and asserts that the task is complete.

参数：

- `conclusion_reasoning: reasoning`：The agent text presenting the final result together with its supporting justification and a completion claim.

成立条件：

- The reasoning presents a specific final value or result as the answer to the task.
- The reasoning links that result to identifiable supporting evidence, such as prior observations, and to any produced output artifact when one was required.
- The reasoning explicitly states that the task is complete or finished.

排除条件：

- The reasoning is intermediate, exploratory, or tentative about the result.
- No final value or result is stated.
- The reasoning only describes steps or plans without asserting completion.
- The stated result is presented only as a candidate still subject to further verification.

### ENUMERATES_COMPETING_EXPLANATIONS

签名：`ENUMERATES_COMPETING_EXPLANATIONS(reasoning: reasoning)`

The reasoning lays out two or more alternative explanations for the same observed situation, treating them as rival candidates whose truth is still to be determined before a course of action is chosen.

参数：

- `reasoning: reasoning`：The reasoning node enumerating the alternative explanations for the observed situation.

成立条件：

- At least two distinct candidate explanations are stated for the same observed condition.
- The alternatives are presented as competing, still-undetermined possibilities rather than as settled findings.

排除条件：

- Only a single explanation is offered.
- The enumerated items are steps of a plan, candidate solutions, or facts about the state rather than rival explanations for why the state is as observed.
- One explanation is already asserted as established, so no genuine competition between alternatives remains.

### ELIMINATES_EXPLANATION_WITH_CONTRARY_EVIDENCE

签名：`ELIMINATES_EXPLANATION_WITH_CONTRARY_EVIDENCE(reasoning: reasoning, observation: observation)`

The reasoning discards a candidate explanation for an observed situation because identifiable content of an observation contradicts a condition that the explanation requires.

参数：

- `reasoning: reasoning`：The reasoning node rejecting the candidate explanation.
- `observation: observation`：The observation whose content contradicts the rejected explanation.

成立条件：

- The reasoning names or clearly refers to a candidate explanation it discards.
- The reasoning cites identifiable observation content that conflicts with what that explanation would require, such as an empty listing contradicting a stash hypothesis or a clean status contradicting an uncommitted-changes hypothesis.

排除条件：

- The reasoning narrows possibilities without stating what rules a candidate out.
- The observation is compatible with the discarded explanation or unrelated to it.
- What is discarded is a candidate solution or artifact rather than an explanation for the observed situation.

### SELECTS_TARGET_AMONG_CANDIDATES

签名：`SELECTS_TARGET_AMONG_CANDIDATES(reasoning: reasoning, observation: observation)`

The reasoning identifies which of several comparable candidate items is the one relevant to the task, justifying the choice with discriminating attributes visible in an observation rather than by position, recency, or surface similarity.

参数：

- `reasoning: reasoning`：The reasoning node comparing the candidates and identifying the relevant one.
- `observation: observation`：The observation exposing the discriminating attributes of the candidates.

成立条件：

- At least two comparable candidate items are distinguished in the reasoning.
- The selection is justified by at least one discriminating attribute visible in the observation, such as provenance, authorship, timestamp, or creation context.
- The reasoning concludes that one candidate is the item relevant to the task.

排除条件：

- Only one candidate is considered, so no discrimination is needed.
- A candidate is chosen by position, recency, or guess without cited discriminating evidence.
- The cited discriminating attribute is not actually present in the observation.

### PREDICTS_OUTCOME_OF_PLANNED_OPERATION

签名：`PREDICTS_OUTCOME_OF_PLANNED_OPERATION(reasoning: reasoning, observation: observation)`

The reasoning forecasts a specific consequence of an operation it has not yet performed, deriving that forecast from identifiable state evidence reported in an observation.

参数：

- `reasoning: reasoning`：The reasoning node naming the planned operation and stating the predicted consequence.
- `observation: observation`：The observation supplying the state evidence on which the forecast rests.

成立条件：

- The reasoning names an operation that is planned but not yet performed.
- A specific expected consequence of that operation is stated, such as an anticipated conflict, failure, or produced change.
- The forecast is tied to identifiable state evidence in the observation.

排除条件：

- The reasoning describes an outcome that has already been observed.
- The forecast is speculation not connected to identifiable state evidence.
- No specific consequence is predicted.
- The observation content cited is unrelated to the predicted consequence.

### DIAGNOSES_ROOT_CAUSE

签名：`DIAGNOSES_ROOT_CAUSE(reasoning: reasoning)`

The reasoning reconstructs a causal account of how an observed state came to be, specifying the preceding events or actions responsible for it rather than merely restating what the state is.

参数：

- `reasoning: reasoning`：The reasoning node presenting the causal reconstruction of the observed state.

成立条件：

- The reasoning specifies one or more preceding events or actions, in sequence, as the cause of the observed condition.
- The account explains why the current state has the observed properties, not merely what those properties are.

排除条件：

- The reasoning only restates the reported problem or the observed state.
- The reasoning lists possible causes without committing to a causal account.
- The reasoning merely paraphrases observed output without identifying the preceding events that produced it.

### ESTABLISHES_CONFLICT_RESOLUTION_PRECEDENCE

签名：`ESTABLISHES_CONFLICT_RESOLUTION_PRECEDENCE(reasoning: reasoning, observation: observation)`

Given an observation showing that two versions of the same artifact conflict, the reasoning decides which version prevails and justifies that choice with a stated precedence rationale rather than an arbitrary pick.

参数：

- `reasoning: reasoning`：The reasoning node choosing the prevailing version and stating the precedence rationale.
- `observation: observation`：The observation exhibiting the conflicting versions of the artifact.

成立条件：

- The observation presents two conflicting alternatives for the same artifact.
- The reasoning selects one alternative as the resulting outcome.
- The reasoning states a rationale for why that alternative supersedes the other, such as which change is newer or which reflects the current situation.

排除条件：

- The reasoning only describes the conflict without selecting a side.
- A side is selected without any stated justification, or purely by position or convenience.
- The observation does not actually show conflicting alternatives for the same artifact.

### PLANS_POST_ACTION_VERIFICATION

签名：`PLANS_POST_ACTION_VERIFICATION(reasoning: reasoning)`

The reasoning explicitly plans one or more checks to be performed after an action in order to determine whether the action produced the required outcome or final state.

参数：

- `reasoning: reasoning`：The reasoning text specifying the future verification checks and their purpose.

成立条件：

- The reasoning refers to future verification or checking steps.
- The checks are directed at confirming the outcome or final state of a completed or planned action, rather than at initial exploration.
- At least one check criterion or target state is identifiable.

排除条件：

- The reasoning only describes exploratory inspection before any relevant action.
- The reasoning only reports checks already completed without planning future verification.
- The reasoning states a general next step without a validation purpose.

### RESOLVES_OBSERVED_CONFLICT_BY_SELECTING_VERSION

签名：`RESOLVES_OBSERVED_CONFLICT_BY_SELECTING_VERSION(conflict_observation: observation, resolution_reasoning: reasoning, resolution_action: action)`

An observation identifies competing alternative contents in a target artifact; the reasoning selects one alternative with an explicit justification; the action applies the selected alternative to resolve the conflict.

参数：

- `conflict_observation: observation`：The observation showing incompatible alternatives, conflict markers, or otherwise competing versions of the target content.
- `resolution_reasoning: reasoning`：The reasoning that selects one competing version and gives a justification for that selection.
- `resolution_action: action`：The action that applies the selected version or otherwise carries out the conflict resolution.

成立条件：

- The observation contains identifiable conflicting or competing content alternatives.
- The reasoning states which alternative is adopted and gives an identifiable semantic reason such as precedence, correctness, or supersession.
- The action implements that selected alternative, for example by adopting, staging, or committing that version.

排除条件：

- The observation does not contain an identifiable conflict or competing versions.
- The reasoning only notes the presence of a conflict without selecting a version.
- The action is unrelated to the selected version or applies a different resolution.
- No justification for the selection is provided.

### DERIVES_EXACTNESS_CONSTRAINT_FROM_MEASUREMENT

签名：`DERIVES_EXACTNESS_CONSTRAINT_FROM_MEASUREMENT(measurement_observation: observation, reasoning: reasoning)`

The reasoning extracts a precise measurable or formatting property from an observation and adopts preservation of that property as a requirement for a subsequent action or acceptance check.

参数：

- `measurement_observation: observation`：The observation reporting an exact quantitative or formatting property such as byte count, hash, whitespace pattern, or exact text layout.
- `reasoning: reasoning`：The reasoning that refers to the precise property as a requirement to be matched or preserved.

成立条件：

- The observation provides a precise measurable, byte-level, or formatting property.
- The reasoning explicitly refers to that property as something that must be matched or preserved.
- The property is used as a constraint on a subsequent action or as an acceptance criterion.

排除条件：

- The observation provides only qualitative or approximate information.
- The reasoning does not impose preservation or matching of the measured property.
- The measured property is mentioned but not used as a requirement or acceptance criterion.

### ACTION_RESULT_CONFIRMS_INTENDED_EFFECT

签名：`ACTION_RESULT_CONFIRMS_INTENDED_EFFECT(action: action, result_observation: observation)`

The observation reports a resulting state that confirms the action achieved its intended effect, rather than merely indicating that the action was invoked or completed.

参数：

- `action: action`：The action whose intended effect is being assessed.
- `result_observation: observation`：The observation reporting the resulting state after the action.

成立条件：

- The observation contains an outcome state that matches the action's intended effect.
- No error or contradictory state undermines that claimed effect.
- The effect is inferred from the reported state, not merely from an acknowledgment that the command was executed.

排除条件：

- The observation only shows that the action was invoked or completed without evidence of its effect.
- The observation reports an error, failure, or incomplete result for the intended effect.
- The observation is unrelated to the action's intended effect.

### LOCATES_TARGET_WITHIN_OBSERVED_STRUCTURE

签名：`LOCATES_TARGET_WITHIN_OBSERVED_STRUCTURE(reasoning: reasoning, observation: observation)`

The reasoning identifies a specific element within a structure, history, or set of records described by an observation as the location, container, or source of a target of interest.

参数：

- `reasoning: reasoning`：The reasoning node pinpointing a specific locus of the target within the observed structure.
- `observation: observation`：The observation describing the structure, history, or set of records being searched.

成立条件：

- The observation describes a structure, history, or set of records with identifiable individual elements.
- The reasoning points to at least one specific element within that observed structure as containing, retaining, or being associated with the target of interest.

排除条件：

- The reasoning only summarizes the observed structure without singling out any element.
- The reasoning states a target value without relating it to a location or record visible in the observation.
- The observation does not contain the structure or records being localized.

### PERSISTS_RECOVERED_VALUE_TO_OUTPUT

签名：`PERSISTS_RECOVERED_VALUE_TO_OUTPUT(action: action, reasoning: reasoning)`

An action writes a specific value that reasoning has identified as recovered or extracted information into the output artifact designated for it, so that the discovered value is preserved outside the search process.

参数：

- `action: action`：The action that writes or creates the designated output artifact.
- `reasoning: reasoning`：The reasoning identifying the recovered value and the output destination where it must be persisted.

成立条件：

- The reasoning identifies a specific value as recovered or extracted and indicates the output location where it should be persisted.
- The action writes that identified value to the indicated output artifact.

排除条件：

- The action writes unrelated, placeholder, or unverified content.
- The reasoning does not identify a recovered value or an output destination.
- The action only reads or inspects information without persisting it.

### APPLIES_REMEDIATION_TO_IDENTIFIED_ARTIFACT

签名：`APPLIES_REMEDIATION_TO_IDENTIFIED_ARTIFACT(action: action, reasoning: reasoning)`

An action performs a removal or elimination operation directed at an unwanted artifact, record, or retention mechanism that the reasoning has identified as the thing to be cleaned up.

参数：

- `action: action`：The action executing the cleanup or removal operation.
- `reasoning: reasoning`：The reasoning identifying the unwanted artifact, record, or retention mechanism and the removal strategy.

成立条件：

- The reasoning identifies a specific unwanted artifact, record, or mechanism that retains it.
- The reasoning indicates a strategy for removing or eliminating that target.
- The action executes an operation directed at that removal rather than at exploration or verification.

排除条件：

- The action is exploratory, diagnostic, or unrelated maintenance.
- The reasoning does not identify an unwanted artifact or retention mechanism.
- The action only checks whether removal is needed without performing removal.
- The action removes state merely for tidiness, with no identified unwanted target.
