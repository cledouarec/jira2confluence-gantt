#! python3

"""
Main script entry point to generate gantt chart.
"""

from jira2confluencegantt.cli import main


if __name__ == "__main__":
    # Entry point of gantt generator script.
    # Execute only if run as a script.
    main()
