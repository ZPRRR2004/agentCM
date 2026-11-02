# 第 1 批 Predicate Discovery 结果

## 一、批次信息

处理 Window：1–5
Prompt 版本：v0001
本批新增谓词：21
本批已有谓词修订：0
当前谓词总数：21

## 二、本批新增谓词

### USES_OBSERVATION_AS_INPUT

签名：`USES_OBSERVATION_AS_INPUT(action: action, observation: observation)`

The action takes an identifiable value or data payload supplied by the specified prior observation and uses it as an operational input to the action's own arguments or payload.

参数：

- `action: action`：The tool invocation whose argument or payload receives the data.
- `observation: observation`：The prior recorded tool result that supplies the value or data payload used by the action.

成立条件：

- The observation is recorded before the receiving action.
- The action's argument or payload can be traced to content of the observation, such as file text reproduced in a write operation or a file name/path used by a later command.
- The traceable item is an operational input of the action, not merely a topic shared with it.

排除条件：

- An observation consulted only to decide which action to perform, without contributing a value or payload to its arguments, does not satisfy this predicate.
- Temporal adjacency, event membership, or a shared subject without an observable input link does not satisfy this predicate.

### USES_REASONING_AS_INPUT

签名：`USES_REASONING_AS_INPUT(action: action, reasoning: reasoning)`

The action performs an operation using concrete content, such as exact text or a command, that the specified prior reasoning node states, so that the reasoning node supplies the material the action commits.

参数：

- `action: action`：The tool invocation that enacts the content declared in the reasoning node.
- `reasoning: reasoning`：The prior agent text that states the concrete content to be used, such as an exact file body or command.

成立条件：

- The reasoning node is recorded before the action.
- The reasoning text states concrete content to be used, not only a general intention, goal, or plan step.
- The action's argument or payload matches that stated content closely enough that the reasoning node is its evident source.

排除条件：

- Reasoning that only expresses an intention or plan step without specifying the content does not satisfy this predicate.
- Reasoning used to judge or evaluate a result, rather than to supply content, does not satisfy this predicate.

### GUIDES_ACTION_CHOICE

签名：`GUIDES_ACTION_CHOICE(observation: observation, action: action)`

The observation reports a diagnostic or probe outcome, such as an error, failure message, or environment/availability result, that is the stated basis for selecting the particular subsequent action or command rather than an alternative.

参数：

- `observation: observation`：The recorded diagnostic or probe result that supplies the decision basis.
- `action: action`：The later tool invocation whose selection is grounded in that diagnostic result.

成立条件：

- The observation precedes the guided action.
- Recorded text links the observation's finding to the choice, such as an error being followed by a corrected command or a reported environment result being cited as grounds for proceeding.
- The later action differs from a previous attempt in a way responsive to the observation.

排除条件：

- An observation that merely provides a data value consumed as an argument does not satisfy this predicate; that is input supply.
- Returning an error without any responsive change in the following action does not satisfy this predicate.
- Calls issued in the same event as the observation cannot be guided by it.

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(action: action, failure: observation)`

The action is performed with the intent of removing a specific defect that is reported or visible in the specified failure observation, by altering the artifact or the command that exhibited the defect.

参数：

- `action: action`：The tool invocation intended to remedy the defect.
- `failure: observation`：The recorded result exhibiting the defect, such as missing proof steps, an error message, or a failed check.

成立条件：

- The failure observation precedes the repair action.
- The defect is identifiable in the failure observation's content, such as placeholder proof holes or an error naming a wrong module or file argument.
- The action's content or arguments are changed to address exactly that defect rather than repeating the prior operation unchanged.

排除条件：

- Re-running an identical operation without addressing the reported defect does not satisfy this predicate.
- An action unrelated to the observed defect does not satisfy this predicate.
- The predicate does not assert that the repair succeeded; success requires a separate confirming result.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, check: observation)`

The check observation reports a result obtained after the repair action on the same subject, and that result shows the defect identified in the failure observation is no longer present.

参数：

- `repair: action`：The remedial action taken against the defect.
- `failure: observation`：The earlier result that exhibited the defect being repaired.
- `check: observation`：The later result that assesses whether the defect persists.

成立条件：

- The failure observation precedes the repair action, and the check observation follows it.
- The check concerns the same subject or version as the failure, such as the same file, command target, or theorem.
- The check reports a success signal for that subject, such as the target artifact being produced cleanly or the compiled theorem being printed without error, rather than another error.

排除条件：

- A check that reports a new or persisting error does not satisfy this predicate.
- A check on an unrelated subject or an earlier version does not satisfy this predicate.
- The repair action alone, without a following successful check result, does not satisfy this predicate.

### DERIVES_CONCLUSION

签名：`DERIVES_CONCLUSION(inputs: observation[], conclusion: reasoning)`

The reasoning node states a verdict or outcome whose substantive basis is the findings reported in the specified observations, which the reasoning text cites.

参数：

- `inputs: observation[]`：The prior recorded results whose findings support the conclusion.
- `conclusion: reasoning`：The agent text stating the resulting verdict or outcome.

成立条件：

- Every cited observation precedes the conclusion text.
- The conclusion text references the specific findings of those observations, such as successful artifact production or successful theorem printing, as the grounds for its verdict.
- The observations are substantive evidence for the verdict, not incidental context.

排除条件：

- Reasoning that proposes forthcoming steps rather than asserting an outcome does not satisfy this predicate.
- A verdict not grounded in the cited observation content, or grounded only in unrecorded expectations, does not satisfy this predicate.
- An observation that merely supplied an argument value does not by itself satisfy this predicate.

### DIAGNOSES_OBSERVED_DEFECT

签名：`DIAGNOSES_OBSERVED_DEFECT(reasoning: reasoning, observation: observation)`

The reasoning node inspects the content of the specified observation and identifies a specific defect or gap in it, explaining what is missing or wrong as a precondition for fixing it.

参数：

- `reasoning: reasoning`：The agent text that states the diagnosis of the defect.
- `observation: observation`：The recorded result whose content contains the defect being diagnosed.

成立条件：

- The observation precedes the diagnosing reasoning text.
- The reasoning text names the specific defective or incomplete element present in the observation content, such as placeholder holes that must be filled or an unresolved subgoal, and indicates what is required.
- The diagnosis refers to the observation's own content rather than to an assumed or future state.

排除条件：

- Reasoning that merely restates or summarizes the observation content without identifying a defect does not satisfy this predicate.
- Reasoning that reports a successful outcome, or that diagnoses something not visible in that observation, does not satisfy this predicate.

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning text states an intended ordered course of forthcoming steps, specifying what will be done next and in what order before results exist.

参数：

- `reasoning: reasoning`：The agent text containing the prospective step sequence.

成立条件：

- The text is future-directed and enumerates or sequences intended actions or subgoals, such as inspecting a file, then completing a proof, then compiling.
- The stated steps are presented as the approach to be carried out, not as completed work.

排除条件：

- Past-tense descriptions of what was already done, or final summaries of results, do not satisfy this predicate.
- A bare statement of the overall task without an intended sequence does not satisfy this predicate.

### EXECUTES_PLANNED_STEP

签名：`EXECUTES_PLANNED_STEP(action: action, reasoning: reasoning)`

The action performs or attempts the concrete operational step that the specified earlier reasoning text presents as an intended course of action, matching the step's described operation and target rather than merely sharing its topic.

参数：

- `action: action`：The recorded tool invocation that performs or attempts the planned step.
- `reasoning: reasoning`：The earlier agent-authored reasoning text that states the intended operational step.

成立条件：

- The reasoning node is recorded before the action and is planning or step-describing text, not the action's own observation and not a report of completed work.
- The reasoning text describes the step concretely enough to identify its operation and target, such as updating package lists, installing named packages, creating an account with a stated shell, writing a file at a stated path, or validating and starting services.
- The action's tool name and arguments correspond to that described operation and target; a plan may contain several steps and this action carries out one of them.

排除条件：

- An action taken for reasons the reasoning never states, or one addressing a different part of the plan, does not satisfy this predicate.
- Topic overlap or event co-occurrence without correspondence between the described step and the action's operation and target does not satisfy this predicate.
- A planned step that no recorded action carries out establishes no instance of this predicate.

### PROVISIONS_OBSERVED_MISSING_COMPONENT

签名：`PROVISIONS_OBSERVED_MISSING_COMPONENT(action: action, observation: observation)`

The action attempts to install, create, or otherwise provision one or more concrete components that the specified earlier observation reported as absent from the environment, so that the observation identifies the provisioning target.

参数：

- `action: action`：The tool invocation that attempts to install, create, or provision the missing components.
- `observation: observation`：The earlier recorded tool result whose content reports the absence of those components.

成立条件：

- The observation's content reports the absence of the component or components, for example a lookup finding no executable for the named tools, or a package, account, or service listing that lacks them.
- The action is a provisioning operation such as package installation, account creation, or service setup, and its arguments name the same components or the packages that provide them.
- The absence-reporting observation precedes the provisioning action; extra dependencies or related packages may be included in the same provisioning action.

排除条件：

- Provisioning a component that no recorded observation reported absent does not satisfy this predicate; the predicate does not rely on inferred absence.
- An action that only inspects availability, or that consumes observed content as an input payload instead of provisioning a missing component, does not satisfy this predicate.
- Remedying a recorded error or failed operation is an attempted-repair mechanism, not this absence-driven provisioning mechanism.
- The predicate does not assert that provisioning succeeded; confirmation of availability would require a separate result.

### USES_REASONING_AS_CRITERION

签名：`USES_REASONING_AS_CRITERION(action: action, reasoning: reasoning)`

The action performs a check whose expected outcome, target value, or acceptance condition is stated in the specified prior reasoning node, so that the reasoning content supplies the standard against which the check's result is judged.

参数：

- `action: action`：The checking tool invocation that performs the verification.
- `reasoning: reasoning`：The prior agent text stating the expected outcome, target value, or acceptance condition for the check.

成立条件：

- The reasoning node is recorded before the checking action.
- The reasoning text states a concrete expected outcome, target value, or acceptance condition for the check, such as the value a requested resource should return or the state constant a probe should find, rather than only announcing that a check will be run.
- The action's tool and arguments test exactly the subject or value named in the stated criterion, so the criterion governs what the check looks for.

排除条件：

- A plan that only announces a check without stating what result would count as acceptable does not satisfy this predicate.
- An expectation taken from the user request rather than from the reasoning node does not satisfy this predicate.
- The observation reporting the check's actual outcome is evidence for the check, not the criterion itself; conclusions drawn from that outcome belong to a different mechanism.
- Passing a value copied from the reasoning into the action's payload without using it as an acceptance standard is input supply, not criterion use.

### DIAGNOSES_FAILURE

签名：`DIAGNOSES_FAILURE(diagnosis: reasoning, failure: observation)`

The reasoning node explains the cause of the failure reported by the specified observation, identifying the condition or earlier step that produced it rather than merely restating the error.

参数：

- `diagnosis: reasoning`：The agent text that explains why the observed operation failed.
- `failure: observation`：The prior recorded result reporting the error, fatal condition, nonzero exit, or contradicting output.

成立条件：

- The failure observation is recorded before the diagnosing reasoning text.
- The observation reports an explicit error, fatal condition, nonzero exit status, or a result that contradicts the expected outcome.
- The reasoning text names a cause for that failure and ties it to observable evidence in the failure output or in the recorded earlier operations that led to the failure.

排除条件：

- Restating or quoting the error message without identifying a causal condition does not satisfy this predicate.
- A reasoning node that only proposes a remedy without explaining why the failure occurred does not satisfy this predicate.
- Explaining an unrelated result, or diagnosing a condition that the specified observation does not report, does not satisfy this predicate.
- Merely pointing out that an item in an observation's content is missing or incomplete, without explaining why an operation failed, does not satisfy this predicate.

### CLEANS_UP_TEST_ARTIFACTS

签名：`CLEANS_UP_TEST_ARTIFACTS(action: action, cleanup_intent: reasoning)`

The action deletes, resets, or empties artifacts that were created solely for verification, returning the environment to its pre-verification state, as the specified prior reasoning node intends.

参数：

- `action: action`：The tool invocation that removes, resets, or empties the verification artifacts.
- `cleanup_intent: reasoning`：The prior agent text stating that verification artifacts are to be removed or that the pre-verification state is to be restored.

成立条件：

- The cleanup-intent reasoning node is recorded before the action and states that artifacts of the verification are to be removed or reset, or that the environment should return to its pre-verification state.
- The action removes, resets, or empties the artifacts named by that intent, such as test credentials, test clones, test commits or branches, or content served during the test, while leaving production configuration in place.
- The removed items are traceable to a verification activity recorded earlier in the trajectory.

排除条件：

- Removing unrelated files, or deleting data that was not created for verification, does not satisfy this predicate.
- An action that remedies a failed operation without removing verification artifacts does not satisfy this predicate.
- Announcing cleanup without a recorded action that removes or resets those artifacts establishes no instance of this predicate.

### EXPLAINS_UNINFORMATIVE_OBSERVATION

签名：`EXPLAINS_UNINFORMATIVE_OBSERVATION(explanation: reasoning, result: observation)`

The reasoning node explains why the specified observation returned no usable output by attributing the deficiency to a property or behavior of the invoked tool or command, so that the empty output is treated as a tool artifact rather than as evidence about the state of the inspected system.

参数：

- `explanation: reasoning`：The agent text that gives the tool-behavior cause for the deficient output.
- `result: observation`：The earlier recorded tool result whose content was empty or lacked the entries the action intended to retrieve.

成立条件：

- The result is recorded before the explanation text and its raw content is empty or omits the entries the corresponding action was meant to retrieve.
- The explanation names a concrete tool-behavior cause, such as a utility lacking a feature, an option that does not follow symbolic links, or a default implementation differing from the one assumed.
- The explanation explicitly separates the tool artifact from evidence about the inspected system, so the absence of output is not read as absence of the inspected state.

排除条件：

- Treating empty or missing output as proof that the inspected resource or state does not exist does not satisfy this predicate.
- An explanation of a genuine target-system failure (service down, file absent, error returned) belongs to failure diagnosis, not to this predicate.
- General discussion of a tool's limitations that is not tied to a specific recorded observation does not satisfy this predicate.

### VERIFIES_REQUESTED_END_TO_END_FLOW

签名：`VERIFIES_REQUESTED_END_TO_END_FLOW(check: action, result: observation)`

The check action exercises the operation the requester asked to be able to perform, through the same client, host, path and payload semantics, after the environment was configured for it; the linked result records the observable outcome of that run, so the requested end-to-end behavior is tested rather than an internal component.

参数：

- `check: action`：The tool invocation that re-runs the requester-specified commands or requests.
- `result: observation`：The recorded outcome of that same run, containing the produced output, transfer messages, or status code.

成立条件：

- The check's arguments reproduce the requester-stated operations with the same client, host, path and payload semantics, in the stated order when a sequence was requested.
- The check is issued after the environment was configured for those operations, and the structural returns edge links it to a recorded result.
- The result records the observable product of the run (produced text, push/clone messages, or an HTTP status) that corresponds to the requester's stated expectation.

排除条件：

- Inspecting a component's own configuration, syntax or process state instead of exercising the requested operation does not satisfy this predicate.
- A run whose arguments were not derived from the requester-stated flow does not satisfy this predicate.
- An action with no recorded result cannot satisfy this predicate, and the predicate does not by itself assert that the verified behavior succeeded.

### USES_REASONING_AS_AUDIT_CHECKLIST

签名：`USES_REASONING_AS_AUDIT_CHECKLIST(action: action, criteria: reasoning)`

The action performs a read-only inspection that gathers the specific set of state items enumerated as things to confirm in the specified prior reasoning node, so that the reasoning supplies the inspection scope rather than an acceptance value.

参数：

- `action: action`：The read-only inspection command that gathers the enumerated state items.
- `criteria: reasoning`：The prior agent text enumerating the state items that must be confirmed.

成立条件：

- The reasoning node is recorded before the action and enumerates multiple distinct state items to confirm, such as named services, ports, repository state, permissions, name resolution, configuration entries or response codes.
- The action's arguments read exactly those enumerated artifacts or subjects and modify none of them.
- The correspondence between each enumerated item and an inspected artifact is traceable from the action's command arguments.

排除条件：

- An inspection of a single item, or one whose items were not enumerated beforehand, does not satisfy this predicate.
- An action that changes state while collecting evidence does not satisfy this predicate.
- A reasoning node that states only a general goal ('check everything is fine') without enumerating the items to confirm does not satisfy this predicate.

### PROVISIONS_SERVICE_AUTORECOVERY

签名：`PROVISIONS_SERVICE_AUTORECOVERY(action: action)`

The action creates or registers a best-effort mechanism that will start a required service or long-running process again if it later stops, addressing anticipated future unavailability rather than a currently observed failure.

参数：

- `action: action`：The tool invocation that creates the recovery helper or wires it into the environment's startup path.

成立条件：

- The action creates a helper that conditionally starts a service only when it is not already running and exits without failing the calling context, and/or registers such a helper in a shell or profile startup path.
- No observation reporting a failure or stoppage of the targeted service precedes the action; the action is not a response to an observed outage.
- The purpose expressed in the accompanying reasoning or file content is preventive best-effort continuity, such as a safety net for restarts.

排除条件：

- Restarting a service after an observed crash or error does not satisfy this predicate; that is an attempted repair of an observed failure.
- Installing a missing package or dependency to fix a current error does not satisfy this predicate.
- Merely claiming future robustness in a summary, without a created or wired mechanism, does not satisfy this predicate.

### PROBES_SUSPECTED_ANOMALY

签名：`PROBES_SUSPECTED_ANOMALY(action: action, hypothesis: reasoning)`

The action gathers targeted evidence about a specific anomaly raised in the specified prior reasoning node in order to establish its cause or whether it has functional consequences, without repairing, removing or reconfiguring the condition being probed.

参数：

- `action: action`：The read-only diagnostic or functional-check invocation aimed at the raised anomaly.
- `hypothesis: reasoning`：The prior agent text that raises the anomaly and states the open question about its cause or impact.

成立条件：

- The reasoning node is recorded before the action and identifies a specific unexpected observation or anomaly together with an unresolved question about its cause or impact.
- The action queries data specific to that anomaly (for example process ancestry and waiting states) or re-exercises the affected capability to see whether it still functions.
- The action does not repair, delete or reconfigure the thing being probed, and the result is left to be interpreted separately.

排除条件：

- An action that fixes or removes the anomaly does not satisfy this predicate.
- A broad multi-item state audit whose inspected items were not selected because of the raised anomaly does not satisfy this predicate.
- A probe whose framing question is not stated in the linked reasoning node does not satisfy this predicate.

### ENCODES_CHECK_AS_SCRIPT

签名：`ENCODES_CHECK_AS_SCRIPT(script_write: action, criteria: reasoning)`

The action writes an executable checker script whose assertions operationalize a set of acceptance criteria stated in the specified reasoning node, so those criteria become runnable tests rather than prose.

参数：

- `script_write: action`：The write invocation that creates or rewrites the checker script.
- `criteria: reasoning`：The prior agent text that enumerates the acceptance checks or conditions the script must implement.

成立条件：

- The criteria reasoning node is recorded before the script-writing action and states concrete checks or acceptance conditions.
- The written content is an executable script that parses or inspects the target subject and contains assertions or comparisons corresponding to those stated checks.
- The script is written to a path and in a form that can be executed by an interpreter.

排除条件：

- Writing a data payload or deliverable file, rather than a checker script, does not satisfy this predicate.
- A script whose checks do not correspond to the criteria stated in the reasoning node does not satisfy this predicate.
- A generic intention to verify something, without identifiable acceptance checks, does not supply the criteria role.

### VERIFIES_WRITTEN_CONTENT

签名：`VERIFIES_WRITTEN_CONTENT(readback: observation, write: action)`

A later read-back observation returns the on-disk content of a file that the specified write action created or overwrote, and the returned content corresponds to the written payload, confirming what was actually persisted.

参数：

- `readback: observation`：The recorded result of reading the file after it was written, containing its raw content.
- `write: action`：The earlier write invocation that created or overwrote that file with a given payload.

成立条件：

- The write action targeted a specific path and had an identifiable payload.
- The readback observation is a later non-error result of reading that same path.
- The returned content reproduces key fields or lines of the written payload, such as identifiers, timestamps, summary, or attendee entries.

排除条件：

- Reading a file that the agent did not write does not satisfy this predicate.
- A read-back whose content differs from the written payload does not satisfy this predicate.
- Inspecting only metadata such as file size or listing does not satisfy this predicate.

### AUDITS_INPUT_INTEGRITY

签名：`AUDITS_INPUT_INTEGRITY(audit: action, purpose: reasoning)`

The action inspects metadata and/or checksums of designated input artifacts so that their unmodified state can be substantiated for the integrity purpose stated in the specified reasoning node.

参数：

- `audit: action`：The invocation that reads file metadata or computes digests over the designated input paths.
- `purpose: reasoning`：The prior agent text that states the intent to confirm the designated read-only inputs remain unmodified.

成立条件：

- The purpose reasoning node is recorded before the audit action and states the intent to confirm that designated read-only input artifacts remain unmodified.
- The audit action's command reads metadata or computes digests over those input paths without modifying them.
- The resulting observation reports the inspected paths, timestamps, sizes, or digests.

排除条件：

- Reading input content for use as data is data acquisition, not an integrity audit.
- A listing or checksum run with no stated integrity purpose does not satisfy this predicate.
- The audit output alone, absent a recorded baseline digest, does not establish that the inputs are unmodified.

## 三、本批已有谓词修订

本批没有修订已有谓词。

## 四、当前完整 Registry

### USES_OBSERVATION_AS_INPUT

签名：`USES_OBSERVATION_AS_INPUT(action: action, observation: observation)`

The action takes an identifiable value or data payload supplied by the specified prior observation and uses it as an operational input to the action's own arguments or payload.

参数：

- `action: action`：The tool invocation whose argument or payload receives the data.
- `observation: observation`：The prior recorded tool result that supplies the value or data payload used by the action.

成立条件：

- The observation is recorded before the receiving action.
- The action's argument or payload can be traced to content of the observation, such as file text reproduced in a write operation or a file name/path used by a later command.
- The traceable item is an operational input of the action, not merely a topic shared with it.

排除条件：

- An observation consulted only to decide which action to perform, without contributing a value or payload to its arguments, does not satisfy this predicate.
- Temporal adjacency, event membership, or a shared subject without an observable input link does not satisfy this predicate.

### USES_REASONING_AS_INPUT

签名：`USES_REASONING_AS_INPUT(action: action, reasoning: reasoning)`

The action performs an operation using concrete content, such as exact text or a command, that the specified prior reasoning node states, so that the reasoning node supplies the material the action commits.

参数：

- `action: action`：The tool invocation that enacts the content declared in the reasoning node.
- `reasoning: reasoning`：The prior agent text that states the concrete content to be used, such as an exact file body or command.

成立条件：

- The reasoning node is recorded before the action.
- The reasoning text states concrete content to be used, not only a general intention, goal, or plan step.
- The action's argument or payload matches that stated content closely enough that the reasoning node is its evident source.

排除条件：

- Reasoning that only expresses an intention or plan step without specifying the content does not satisfy this predicate.
- Reasoning used to judge or evaluate a result, rather than to supply content, does not satisfy this predicate.

### GUIDES_ACTION_CHOICE

签名：`GUIDES_ACTION_CHOICE(observation: observation, action: action)`

The observation reports a diagnostic or probe outcome, such as an error, failure message, or environment/availability result, that is the stated basis for selecting the particular subsequent action or command rather than an alternative.

参数：

- `observation: observation`：The recorded diagnostic or probe result that supplies the decision basis.
- `action: action`：The later tool invocation whose selection is grounded in that diagnostic result.

成立条件：

- The observation precedes the guided action.
- Recorded text links the observation's finding to the choice, such as an error being followed by a corrected command or a reported environment result being cited as grounds for proceeding.
- The later action differs from a previous attempt in a way responsive to the observation.

排除条件：

- An observation that merely provides a data value consumed as an argument does not satisfy this predicate; that is input supply.
- Returning an error without any responsive change in the following action does not satisfy this predicate.
- Calls issued in the same event as the observation cannot be guided by it.

### ATTEMPTS_REPAIR

签名：`ATTEMPTS_REPAIR(action: action, failure: observation)`

The action is performed with the intent of removing a specific defect that is reported or visible in the specified failure observation, by altering the artifact or the command that exhibited the defect.

参数：

- `action: action`：The tool invocation intended to remedy the defect.
- `failure: observation`：The recorded result exhibiting the defect, such as missing proof steps, an error message, or a failed check.

成立条件：

- The failure observation precedes the repair action.
- The defect is identifiable in the failure observation's content, such as placeholder proof holes or an error naming a wrong module or file argument.
- The action's content or arguments are changed to address exactly that defect rather than repeating the prior operation unchanged.

排除条件：

- Re-running an identical operation without addressing the reported defect does not satisfy this predicate.
- An action unrelated to the observed defect does not satisfy this predicate.
- The predicate does not assert that the repair succeeded; success requires a separate confirming result.

### CONFIRMS_REPAIR

签名：`CONFIRMS_REPAIR(repair: action, failure: observation, check: observation)`

The check observation reports a result obtained after the repair action on the same subject, and that result shows the defect identified in the failure observation is no longer present.

参数：

- `repair: action`：The remedial action taken against the defect.
- `failure: observation`：The earlier result that exhibited the defect being repaired.
- `check: observation`：The later result that assesses whether the defect persists.

成立条件：

- The failure observation precedes the repair action, and the check observation follows it.
- The check concerns the same subject or version as the failure, such as the same file, command target, or theorem.
- The check reports a success signal for that subject, such as the target artifact being produced cleanly or the compiled theorem being printed without error, rather than another error.

排除条件：

- A check that reports a new or persisting error does not satisfy this predicate.
- A check on an unrelated subject or an earlier version does not satisfy this predicate.
- The repair action alone, without a following successful check result, does not satisfy this predicate.

### DERIVES_CONCLUSION

签名：`DERIVES_CONCLUSION(inputs: observation[], conclusion: reasoning)`

The reasoning node states a verdict or outcome whose substantive basis is the findings reported in the specified observations, which the reasoning text cites.

参数：

- `inputs: observation[]`：The prior recorded results whose findings support the conclusion.
- `conclusion: reasoning`：The agent text stating the resulting verdict or outcome.

成立条件：

- Every cited observation precedes the conclusion text.
- The conclusion text references the specific findings of those observations, such as successful artifact production or successful theorem printing, as the grounds for its verdict.
- The observations are substantive evidence for the verdict, not incidental context.

排除条件：

- Reasoning that proposes forthcoming steps rather than asserting an outcome does not satisfy this predicate.
- A verdict not grounded in the cited observation content, or grounded only in unrecorded expectations, does not satisfy this predicate.
- An observation that merely supplied an argument value does not by itself satisfy this predicate.

### DIAGNOSES_OBSERVED_DEFECT

签名：`DIAGNOSES_OBSERVED_DEFECT(reasoning: reasoning, observation: observation)`

The reasoning node inspects the content of the specified observation and identifies a specific defect or gap in it, explaining what is missing or wrong as a precondition for fixing it.

参数：

- `reasoning: reasoning`：The agent text that states the diagnosis of the defect.
- `observation: observation`：The recorded result whose content contains the defect being diagnosed.

成立条件：

- The observation precedes the diagnosing reasoning text.
- The reasoning text names the specific defective or incomplete element present in the observation content, such as placeholder holes that must be filled or an unresolved subgoal, and indicates what is required.
- The diagnosis refers to the observation's own content rather than to an assumed or future state.

排除条件：

- Reasoning that merely restates or summarizes the observation content without identifying a defect does not satisfy this predicate.
- Reasoning that reports a successful outcome, or that diagnoses something not visible in that observation, does not satisfy this predicate.

### IS_PLAN

签名：`IS_PLAN(reasoning: reasoning)`

The reasoning text states an intended ordered course of forthcoming steps, specifying what will be done next and in what order before results exist.

参数：

- `reasoning: reasoning`：The agent text containing the prospective step sequence.

成立条件：

- The text is future-directed and enumerates or sequences intended actions or subgoals, such as inspecting a file, then completing a proof, then compiling.
- The stated steps are presented as the approach to be carried out, not as completed work.

排除条件：

- Past-tense descriptions of what was already done, or final summaries of results, do not satisfy this predicate.
- A bare statement of the overall task without an intended sequence does not satisfy this predicate.

### EXECUTES_PLANNED_STEP

签名：`EXECUTES_PLANNED_STEP(action: action, reasoning: reasoning)`

The action performs or attempts the concrete operational step that the specified earlier reasoning text presents as an intended course of action, matching the step's described operation and target rather than merely sharing its topic.

参数：

- `action: action`：The recorded tool invocation that performs or attempts the planned step.
- `reasoning: reasoning`：The earlier agent-authored reasoning text that states the intended operational step.

成立条件：

- The reasoning node is recorded before the action and is planning or step-describing text, not the action's own observation and not a report of completed work.
- The reasoning text describes the step concretely enough to identify its operation and target, such as updating package lists, installing named packages, creating an account with a stated shell, writing a file at a stated path, or validating and starting services.
- The action's tool name and arguments correspond to that described operation and target; a plan may contain several steps and this action carries out one of them.

排除条件：

- An action taken for reasons the reasoning never states, or one addressing a different part of the plan, does not satisfy this predicate.
- Topic overlap or event co-occurrence without correspondence between the described step and the action's operation and target does not satisfy this predicate.
- A planned step that no recorded action carries out establishes no instance of this predicate.

### PROVISIONS_OBSERVED_MISSING_COMPONENT

签名：`PROVISIONS_OBSERVED_MISSING_COMPONENT(action: action, observation: observation)`

The action attempts to install, create, or otherwise provision one or more concrete components that the specified earlier observation reported as absent from the environment, so that the observation identifies the provisioning target.

参数：

- `action: action`：The tool invocation that attempts to install, create, or provision the missing components.
- `observation: observation`：The earlier recorded tool result whose content reports the absence of those components.

成立条件：

- The observation's content reports the absence of the component or components, for example a lookup finding no executable for the named tools, or a package, account, or service listing that lacks them.
- The action is a provisioning operation such as package installation, account creation, or service setup, and its arguments name the same components or the packages that provide them.
- The absence-reporting observation precedes the provisioning action; extra dependencies or related packages may be included in the same provisioning action.

排除条件：

- Provisioning a component that no recorded observation reported absent does not satisfy this predicate; the predicate does not rely on inferred absence.
- An action that only inspects availability, or that consumes observed content as an input payload instead of provisioning a missing component, does not satisfy this predicate.
- Remedying a recorded error or failed operation is an attempted-repair mechanism, not this absence-driven provisioning mechanism.
- The predicate does not assert that provisioning succeeded; confirmation of availability would require a separate result.

### USES_REASONING_AS_CRITERION

签名：`USES_REASONING_AS_CRITERION(action: action, reasoning: reasoning)`

The action performs a check whose expected outcome, target value, or acceptance condition is stated in the specified prior reasoning node, so that the reasoning content supplies the standard against which the check's result is judged.

参数：

- `action: action`：The checking tool invocation that performs the verification.
- `reasoning: reasoning`：The prior agent text stating the expected outcome, target value, or acceptance condition for the check.

成立条件：

- The reasoning node is recorded before the checking action.
- The reasoning text states a concrete expected outcome, target value, or acceptance condition for the check, such as the value a requested resource should return or the state constant a probe should find, rather than only announcing that a check will be run.
- The action's tool and arguments test exactly the subject or value named in the stated criterion, so the criterion governs what the check looks for.

排除条件：

- A plan that only announces a check without stating what result would count as acceptable does not satisfy this predicate.
- An expectation taken from the user request rather than from the reasoning node does not satisfy this predicate.
- The observation reporting the check's actual outcome is evidence for the check, not the criterion itself; conclusions drawn from that outcome belong to a different mechanism.
- Passing a value copied from the reasoning into the action's payload without using it as an acceptance standard is input supply, not criterion use.

### DIAGNOSES_FAILURE

签名：`DIAGNOSES_FAILURE(diagnosis: reasoning, failure: observation)`

The reasoning node explains the cause of the failure reported by the specified observation, identifying the condition or earlier step that produced it rather than merely restating the error.

参数：

- `diagnosis: reasoning`：The agent text that explains why the observed operation failed.
- `failure: observation`：The prior recorded result reporting the error, fatal condition, nonzero exit, or contradicting output.

成立条件：

- The failure observation is recorded before the diagnosing reasoning text.
- The observation reports an explicit error, fatal condition, nonzero exit status, or a result that contradicts the expected outcome.
- The reasoning text names a cause for that failure and ties it to observable evidence in the failure output or in the recorded earlier operations that led to the failure.

排除条件：

- Restating or quoting the error message without identifying a causal condition does not satisfy this predicate.
- A reasoning node that only proposes a remedy without explaining why the failure occurred does not satisfy this predicate.
- Explaining an unrelated result, or diagnosing a condition that the specified observation does not report, does not satisfy this predicate.
- Merely pointing out that an item in an observation's content is missing or incomplete, without explaining why an operation failed, does not satisfy this predicate.

### CLEANS_UP_TEST_ARTIFACTS

签名：`CLEANS_UP_TEST_ARTIFACTS(action: action, cleanup_intent: reasoning)`

The action deletes, resets, or empties artifacts that were created solely for verification, returning the environment to its pre-verification state, as the specified prior reasoning node intends.

参数：

- `action: action`：The tool invocation that removes, resets, or empties the verification artifacts.
- `cleanup_intent: reasoning`：The prior agent text stating that verification artifacts are to be removed or that the pre-verification state is to be restored.

成立条件：

- The cleanup-intent reasoning node is recorded before the action and states that artifacts of the verification are to be removed or reset, or that the environment should return to its pre-verification state.
- The action removes, resets, or empties the artifacts named by that intent, such as test credentials, test clones, test commits or branches, or content served during the test, while leaving production configuration in place.
- The removed items are traceable to a verification activity recorded earlier in the trajectory.

排除条件：

- Removing unrelated files, or deleting data that was not created for verification, does not satisfy this predicate.
- An action that remedies a failed operation without removing verification artifacts does not satisfy this predicate.
- Announcing cleanup without a recorded action that removes or resets those artifacts establishes no instance of this predicate.

### EXPLAINS_UNINFORMATIVE_OBSERVATION

签名：`EXPLAINS_UNINFORMATIVE_OBSERVATION(explanation: reasoning, result: observation)`

The reasoning node explains why the specified observation returned no usable output by attributing the deficiency to a property or behavior of the invoked tool or command, so that the empty output is treated as a tool artifact rather than as evidence about the state of the inspected system.

参数：

- `explanation: reasoning`：The agent text that gives the tool-behavior cause for the deficient output.
- `result: observation`：The earlier recorded tool result whose content was empty or lacked the entries the action intended to retrieve.

成立条件：

- The result is recorded before the explanation text and its raw content is empty or omits the entries the corresponding action was meant to retrieve.
- The explanation names a concrete tool-behavior cause, such as a utility lacking a feature, an option that does not follow symbolic links, or a default implementation differing from the one assumed.
- The explanation explicitly separates the tool artifact from evidence about the inspected system, so the absence of output is not read as absence of the inspected state.

排除条件：

- Treating empty or missing output as proof that the inspected resource or state does not exist does not satisfy this predicate.
- An explanation of a genuine target-system failure (service down, file absent, error returned) belongs to failure diagnosis, not to this predicate.
- General discussion of a tool's limitations that is not tied to a specific recorded observation does not satisfy this predicate.

### VERIFIES_REQUESTED_END_TO_END_FLOW

签名：`VERIFIES_REQUESTED_END_TO_END_FLOW(check: action, result: observation)`

The check action exercises the operation the requester asked to be able to perform, through the same client, host, path and payload semantics, after the environment was configured for it; the linked result records the observable outcome of that run, so the requested end-to-end behavior is tested rather than an internal component.

参数：

- `check: action`：The tool invocation that re-runs the requester-specified commands or requests.
- `result: observation`：The recorded outcome of that same run, containing the produced output, transfer messages, or status code.

成立条件：

- The check's arguments reproduce the requester-stated operations with the same client, host, path and payload semantics, in the stated order when a sequence was requested.
- The check is issued after the environment was configured for those operations, and the structural returns edge links it to a recorded result.
- The result records the observable product of the run (produced text, push/clone messages, or an HTTP status) that corresponds to the requester's stated expectation.

排除条件：

- Inspecting a component's own configuration, syntax or process state instead of exercising the requested operation does not satisfy this predicate.
- A run whose arguments were not derived from the requester-stated flow does not satisfy this predicate.
- An action with no recorded result cannot satisfy this predicate, and the predicate does not by itself assert that the verified behavior succeeded.

### USES_REASONING_AS_AUDIT_CHECKLIST

签名：`USES_REASONING_AS_AUDIT_CHECKLIST(action: action, criteria: reasoning)`

The action performs a read-only inspection that gathers the specific set of state items enumerated as things to confirm in the specified prior reasoning node, so that the reasoning supplies the inspection scope rather than an acceptance value.

参数：

- `action: action`：The read-only inspection command that gathers the enumerated state items.
- `criteria: reasoning`：The prior agent text enumerating the state items that must be confirmed.

成立条件：

- The reasoning node is recorded before the action and enumerates multiple distinct state items to confirm, such as named services, ports, repository state, permissions, name resolution, configuration entries or response codes.
- The action's arguments read exactly those enumerated artifacts or subjects and modify none of them.
- The correspondence between each enumerated item and an inspected artifact is traceable from the action's command arguments.

排除条件：

- An inspection of a single item, or one whose items were not enumerated beforehand, does not satisfy this predicate.
- An action that changes state while collecting evidence does not satisfy this predicate.
- A reasoning node that states only a general goal ('check everything is fine') without enumerating the items to confirm does not satisfy this predicate.

### PROVISIONS_SERVICE_AUTORECOVERY

签名：`PROVISIONS_SERVICE_AUTORECOVERY(action: action)`

The action creates or registers a best-effort mechanism that will start a required service or long-running process again if it later stops, addressing anticipated future unavailability rather than a currently observed failure.

参数：

- `action: action`：The tool invocation that creates the recovery helper or wires it into the environment's startup path.

成立条件：

- The action creates a helper that conditionally starts a service only when it is not already running and exits without failing the calling context, and/or registers such a helper in a shell or profile startup path.
- No observation reporting a failure or stoppage of the targeted service precedes the action; the action is not a response to an observed outage.
- The purpose expressed in the accompanying reasoning or file content is preventive best-effort continuity, such as a safety net for restarts.

排除条件：

- Restarting a service after an observed crash or error does not satisfy this predicate; that is an attempted repair of an observed failure.
- Installing a missing package or dependency to fix a current error does not satisfy this predicate.
- Merely claiming future robustness in a summary, without a created or wired mechanism, does not satisfy this predicate.

### PROBES_SUSPECTED_ANOMALY

签名：`PROBES_SUSPECTED_ANOMALY(action: action, hypothesis: reasoning)`

The action gathers targeted evidence about a specific anomaly raised in the specified prior reasoning node in order to establish its cause or whether it has functional consequences, without repairing, removing or reconfiguring the condition being probed.

参数：

- `action: action`：The read-only diagnostic or functional-check invocation aimed at the raised anomaly.
- `hypothesis: reasoning`：The prior agent text that raises the anomaly and states the open question about its cause or impact.

成立条件：

- The reasoning node is recorded before the action and identifies a specific unexpected observation or anomaly together with an unresolved question about its cause or impact.
- The action queries data specific to that anomaly (for example process ancestry and waiting states) or re-exercises the affected capability to see whether it still functions.
- The action does not repair, delete or reconfigure the thing being probed, and the result is left to be interpreted separately.

排除条件：

- An action that fixes or removes the anomaly does not satisfy this predicate.
- A broad multi-item state audit whose inspected items were not selected because of the raised anomaly does not satisfy this predicate.
- A probe whose framing question is not stated in the linked reasoning node does not satisfy this predicate.

### ENCODES_CHECK_AS_SCRIPT

签名：`ENCODES_CHECK_AS_SCRIPT(script_write: action, criteria: reasoning)`

The action writes an executable checker script whose assertions operationalize a set of acceptance criteria stated in the specified reasoning node, so those criteria become runnable tests rather than prose.

参数：

- `script_write: action`：The write invocation that creates or rewrites the checker script.
- `criteria: reasoning`：The prior agent text that enumerates the acceptance checks or conditions the script must implement.

成立条件：

- The criteria reasoning node is recorded before the script-writing action and states concrete checks or acceptance conditions.
- The written content is an executable script that parses or inspects the target subject and contains assertions or comparisons corresponding to those stated checks.
- The script is written to a path and in a form that can be executed by an interpreter.

排除条件：

- Writing a data payload or deliverable file, rather than a checker script, does not satisfy this predicate.
- A script whose checks do not correspond to the criteria stated in the reasoning node does not satisfy this predicate.
- A generic intention to verify something, without identifiable acceptance checks, does not supply the criteria role.

### VERIFIES_WRITTEN_CONTENT

签名：`VERIFIES_WRITTEN_CONTENT(readback: observation, write: action)`

A later read-back observation returns the on-disk content of a file that the specified write action created or overwrote, and the returned content corresponds to the written payload, confirming what was actually persisted.

参数：

- `readback: observation`：The recorded result of reading the file after it was written, containing its raw content.
- `write: action`：The earlier write invocation that created or overwrote that file with a given payload.

成立条件：

- The write action targeted a specific path and had an identifiable payload.
- The readback observation is a later non-error result of reading that same path.
- The returned content reproduces key fields or lines of the written payload, such as identifiers, timestamps, summary, or attendee entries.

排除条件：

- Reading a file that the agent did not write does not satisfy this predicate.
- A read-back whose content differs from the written payload does not satisfy this predicate.
- Inspecting only metadata such as file size or listing does not satisfy this predicate.

### AUDITS_INPUT_INTEGRITY

签名：`AUDITS_INPUT_INTEGRITY(audit: action, purpose: reasoning)`

The action inspects metadata and/or checksums of designated input artifacts so that their unmodified state can be substantiated for the integrity purpose stated in the specified reasoning node.

参数：

- `audit: action`：The invocation that reads file metadata or computes digests over the designated input paths.
- `purpose: reasoning`：The prior agent text that states the intent to confirm the designated read-only inputs remain unmodified.

成立条件：

- The purpose reasoning node is recorded before the audit action and states the intent to confirm that designated read-only input artifacts remain unmodified.
- The audit action's command reads metadata or computes digests over those input paths without modifying them.
- The resulting observation reports the inspected paths, timestamps, sizes, or digests.

排除条件：

- Reading input content for use as data is data acquisition, not an integrity audit.
- A listing or checksum run with no stated integrity purpose does not satisfy this predicate.
- The audit output alone, absent a recorded baseline digest, does not establish that the inputs are unmodified.
