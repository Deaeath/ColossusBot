# File: commands/helpers/progress_bar.py

"""
ProgressBar Utility Class: Generate and Format Progress Bars
------------------------------------------------------------
This utility class allows for the creation of progress bars, useful for 
displaying task progress in the Discord bot. It includes functionality 
for both a basic progress bar and one that includes a percentage.
"""

class ProgressBar:
    """
    A utility class for generating progress bars.
    """

    def __init__(self, total: int, bar_length: int = 20) -> None:
        """
        Initializes the ProgressBar instance.

        :param total: The total value for the progress bar.
        :param bar_length: The length of the progress bar (default is 20).
        """
        if total <= 0:
            raise ValueError("Total must be greater than 0.")
        self.total = total
        self.bar_length = bar_length

    def create(self, current: int) -> str:
        """
        Creates a progress bar for the given current progress.

        :param current: The current progress value.
        :return: A string representing the progress bar.
        """
        if current < 0:
            raise ValueError("Current progress cannot be negative.")
        if current > self.total:
            raise ValueError("Current progress cannot exceed total.")

        progress = float(current) / float(self.total)
        filled_length = int(round(progress * self.bar_length))
        arrow = '#' * filled_length
        spaces = '-' * (self.bar_length - filled_length)
        return f"[{arrow}{spaces}]"

    def with_percentage(self, current: int) -> str:
        """
        Creates a progress bar with a percentage displayed alongside it.

        :param current: The current progress value.
        :return: A string representing the progress bar with percentage.
        """
        progress_bar = self.create(current)
        percentage = (current / self.total) * 100
        return f"{progress_bar} {percentage:.2f}%"
