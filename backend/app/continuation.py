"""Finite in-process continuation for verified budget-only progress, never errors."""

from dataclasses import dataclass


@dataclass
class BudgetProgress(Exception):
    stage: str
    completed: int
    total: int
    halt: bool = (
        False  # wall-clock slice guard: stop this invocation, never continue in-process
    )


def continue_budgeted(step, job, max_slices=256):
    previous = {}
    for _ in range(max_slices):
        try:
            return step()
        except BudgetProgress as pause:
            if pause.halt:
                job.text(
                    f"\nSlice time guard reached at {pause.stage}: {pause.completed}/{pause.total} saved. Not continuing automatically; resume explicitly.\n"
                )
                return None
            if not (
                0 < pause.completed < pause.total
            ) or pause.completed <= previous.get(pause.stage, 0):
                job.text(
                    "\nAutomatic continuation stopped: no verified budget-only progress. Checkpoints retained.\n"
                )
                return None
            previous[pause.stage] = pause.completed
            job.text(
                f"\nContinuing {pause.stage}: {pause.completed}/{pause.total} saved.\n"
            )
    job.text(
        "\nAutomatic continuation safety limit reached. Checkpoints retained; resume explicitly to continue.\n"
    )
    return None
