# This Journal gets updated automatically by the Journal Logger Agent

### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 12:57
- **Prompt**: read #copilot-instructions and #journal-logger.agent
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 12:57
- **User**:  justin.d-costa@epita.fr
- **Prompt**: read #copilot-instructions and #journal-logger.agent
- **CoPilot Mode**: Agent
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Read instruction files; no code changes.
- **Context and Reasons for Changes**: User requested loading instruction documents to align behavior for this session.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 12:58
- **Prompt**: Create a local git repo for this project
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 12:58
- **User**:  justin.d-costa@epita.fr
- **Prompt**: Create a local git repo for this project
- **CoPilot Mode**: Agent
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Initialized a local Git repository and verified repo status.
- **Context and Reasons for Changes**: User requested local git setup for the current project folder.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 12:59
- **Prompt**: do a git add . and then do a initial commit with the message: "Initial Commit"
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 13:01
- **User**:  justin.d-costa@epita.fr
- **Prompt**: do a git add .
and then do a initial commit with the message: "Initial Commit"
- **CoPilot Mode**: Agent
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Ran git add ., attempted commit, then created commit with message "Initial Commit" using --allow-empty because working tree was already clean.
- **Context and Reasons for Changes**: User requested staging and an initial commit with exact message.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 13:08
- **Prompt**: "a simple python application that will displays 10 squares moving around randomly on the canvas" help me implement this with stubs and todos in main.py
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 13:10
- **User**:  justin.d-costa@epita.fr
- **Prompt**: "a simple python application that will displays 10 squares moving around randomly on the canvas"
help me implement this with stubs and todos in main.py
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Added a runnable pygame scaffold in main.py with structured stub functions and TODOs for square movement behavior.
- **Context and Reasons for Changes**: User requested implementation help via starter code rather than a fully finished solution.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 13:34
- **Prompt**: I have made the changes and I want you to write the tests for it to check if they work correctly
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 13:42
- **User**:  justin.d-costa@epita.fr
- **Prompt**: I have made the changes and I want you to write the tests for it to check if they work correctly
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Created comprehensive test_main.py with 27 test cases covering all functions, fixtures, edge cases, and integration scenarios. All tests pass.
- **Context and Reasons for Changes**: User provided implementation changes (per-square colors, random drift, improved edge clamping) and requested test coverage. Tests verify correctness of the implementation.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 13:45
- **Prompt**: clean up the code. Optimise it. and remove the comments such as todos and the stubs. also make sure to run the test after to check if the code works.
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 13:46
- **User**:  justin.d-costa@epita.fr
- **Prompt**: clean up the code. Optimise it. and remove the comments such as todos and the stubs.
also make sure to run the test after to check if the code works.
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Refactored main.py to remove stub/TODO wording, extracted constants, simplified square creation, extracted boundary handling helper, and kept behavior-compatible movement/drift logic. Ran tests successfully.
- **Context and Reasons for Changes**: User requested cleanup and optimization with post-change test verification.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 13:47
- **Prompt**: Create a Readme.md file that clearly explains how to run the application and also about the function of the application. Be detailed.
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 13:48
- **User**:  justin.d-costa@epita.fr
- **Prompt**: Create a Readme.md file that clearly explains how to run the application and also about the function of the application. Be detailed.
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Added a detailed README.md with application purpose, architecture, setup, run commands, test commands, troubleshooting, and enhancement ideas.
- **Context and Reasons for Changes**: User requested clear and detailed documentation for running and understanding the application.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 14:06
- **Prompt**: Make the blocks different sizes and improve the ui and graphics.
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 14:08
- **User**:  justin.d-costa@epita.fr
- **Prompt**: Make the blocks different sizes and improve the ui and graphics.
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Added variable square sizes, gradient background, glow/border/shine styling for blocks, and updated tests to validate variable-size bounds and improved pygame Rect mocking.
- **Context and Reasons for Changes**: User requested visual and graphics enhancements with different block sizes while keeping behavior correct.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 14:28
- **Prompt**: have it a clock and configuaration setting in window to change speed add more blocks, increase block sizes, option to make the blocks interactable(as in can have collisions between 2 or more blocks).
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 14:31
- **User**:  justin.d-costa@epita.fr
- **Prompt**: have it a clock and configuaration setting in window to change speed add more blocks, increase block sizes, option to make the blocks interactable(as in can have collisions between 2 or more blocks).
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Added in-window clock, keyboard-driven configuration overlay, dynamic speed/block-count/size controls, optional block collisions with resolution logic, and expanded tests for the new runtime features.
- **Context and Reasons for Changes**: User requested richer runtime controls and optional inter-block interaction while preserving existing animation behavior.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 14:36
- **Prompt**: revert back to original one without the clock and these features as i will manually add them myself.
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 14:37
- **User**:  justin.d-costa@epita.fr
- **Prompt**: revert back to original one without the clock and these features as i will manually add them myself.
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Restored main.py and test_main.py to pre-clock/config/collision baseline and verified tests pass in both pytest and direct file execution modes.
- **Context and Reasons for Changes**: User requested rollback to the simpler original version to manually implement advanced features.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 14:43
- **Prompt**: check my code and the changes i made. check it out with the tests and see if everything works out.
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 14:44
- **User**:  justin.d-costa@epita.fr
- **Prompt**: check my code and the changes i made.
check it out with the tests and see if everything works out.
- **CoPilot Mode**: Agent
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Reviewed current main.py changes (100 squares and per-square max_speed cap), executed test suite via pytest and direct test file execution, and performed an additional runtime sanity attempt.
- **Context and Reasons for Changes**: User requested validation of recent code changes and verification via tests; no source code edits were made.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 14:47
- **Prompt**: I dont want the jittering and want them to move straight update the code
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 14:48
- **User**:  justin.d-costa@epita.fr
- **Prompt**: I dont want the jittering and want them to move straight
update the code
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Removed random velocity drift from update_square so blocks move in straight lines, and updated drift-related tests to assert constant velocity motion.
- **Context and Reasons for Changes**: User requested smooth straight movement without jittering.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 14:57
- **Prompt**: Jitter - Make each square change its direction randomly a little bit over time.
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 14:59
- **User**:  justin.d-costa@epita.fr
- **Prompt**: Jitter - Make each square change its direction randomly a little bit over time.
- **CoPilot Mode**: Edit
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Reintroduced subtle random jitter in update_square with velocity clamping to each square's max_speed, and updated tests to validate deterministic jitter behavior.
- **Context and Reasons for Changes**: User requested small random direction changes over time to bring back jitter motion.


### **New Interaction**
- **Hook Version**: 1.02
- **Date**: 30-03-2026 15:21
- **Prompt**: I have updated the report.md file. commit it and push it to github
### **New Interaction**
- **Agent Version**: 2.2
- **Date**: 30-03-2026 15:21
- **User**:  justin.d-costa@epita.fr
- **Prompt**: I have updated the report.md file.
commit it and push it to github
- **CoPilot Mode**: Agent
- **CoPilot Model**: GPT-5.3-Codex
- **Socratic Mode**: ON
- **Changes Made**: Staged and committed the updated report, then pushed to GitHub.
- **Context and Reasons for Changes**: User requested committing and pushing the updated report file.

