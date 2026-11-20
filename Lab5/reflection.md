# Reflection

> The handout text I could extract did not list the four reflection questions, so these are the usual ones for this lab. Swap the headings if yours differ.

**1. Which tool was most useful, and why?**
Pylint, because it found the most (bare except, mutable default, global, resource leaks) and took the score from 5.60 to 10. Bandit was the most important for risk: its single High finding (`os.system` with a concatenated string) was a real command injection hole.

**2. Did any tool give false positives or miss something?**
None of the findings were wrong, but the tools missed logic bugs entirely: reversed slot `14-12`, integer slot `1530`, equipment going negative, and double-bookings that are logged but still accepted. Those only show up by reading or running the code.

**3. How do the tools complement each other?**
Flake8 enforces formatting and catches unused variables, Pylint judges design and correctness, Bandit looks only at security. Some issues overlap (bare `except` appears in all three), which confirms its importance.

**4. How would you use static analysis in a real project?**
Run all three in CI and as a pre-commit hook, fail the build on Bandit High/Medium and on Pylint dropping below a threshold, and pair them with unit tests for the logic errors they cannot see.
