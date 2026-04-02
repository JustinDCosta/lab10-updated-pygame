Project Report: AI-Assisted Development

1. Initial Approach
Understanding: My strategy was to use AI as a scaffolding and review tool, rather than just having it write the whole app for me. I wanted to build a Pygame app with moving squares, so I specifically prompted Copilot to generate the initial file with stubs and TODO comments. My plan was to write the core movement and collision logic myself, and then lean on AI later for testing and adding complex features.

2. Prompting & AI Interaction
Successes: Prompting for stubs and TODOs worked perfectly and gave me a great structure to start coding. After I implemented the base logic, having Copilot review my code and generate tests was a huge time-saver. It also did a really good job when I prompted it to add specific new features, like adding random "jitter" to the movement, increasing the square count to 100, and implementing a min/max scale where speed is tied to block size (bigger blocks move slower). Latest changes: I made a few extra changes without AI help. I only used AI for checking, grammar corrections, and comment logic.

3. Key Learnings
Technical Skills: On the coding side, I learned how to implement basic physics logic (tying speed limits to object size). On the system side, I learned way more about Python environments than I planned to. I now understand what a virtual environment (.venv) is, how packages get built, and that sometimes you literally cannot force a package to install. The correct developer move is often to downgrade to a stable version (like Python 3.13) rather than fighting a wall of red text. I also learned from my professor that I can press Ctrl and click a function to jump directly to its code in VS Code. Latest changes: AI can create a project, but not perfectly, and it should be used under close supervision. For now, it can make mistakes if it is not prompted or guided correctly. You should always verify the code.

AI Workflow: This project proved that using AI to generate stubs, review code, and write tests is an incredibly strong workflow. In my next project, I will definitely keep using it in that way.