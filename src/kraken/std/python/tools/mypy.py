from __future__ import annotations

from pathlib import Path
from typing import Any

from kraken.core import Project, Property, TaskResult

from ..settings import EnvironmentAwareDispatchTask


class MypyTask(EnvironmentAwareDispatchTask):
    config_file: Property[Path]
    additional_args: Property[list[str]] = Property.config(default_factory=list)
    check_tests: Property[bool] = Property.config(default=True)
    use_daemon: Property[bool] = Property.config(default=True)

    def get_execute_command(self) -> list[str] | TaskResult:
        # TODO (@NiklasRosenstein): Should we somewhere add a task that ensures `.dmypy.json` is in `.gitignore`?
        #       Having it in the project directory makes it easier to just stop the daemon if it malfunctions (which
        #       happens regularly but is hard to detect automatically).
        status_file = self.project.directory / ".dmypy.json"
        command = ["dmypy", "--status-file", str(status_file), "run", "--"] if self.use_daemon.get() else ["mypy"]
        if self.config_file.is_filled():
            command += ["--config-file", str(self.config_file.get())]
        else:
            command += ["--show-error-codes", "--namespace-packages"]  # Sane defaults. 🙏
        command += ["src/"]
        if self.check_tests.get():
            command += self.settings.get_tests_directory_as_args()
        command += self.additional_args.get()
        return command


def mypy(project: Project | None = None, **kwargs: Any) -> MypyTask:
    project = project or Project.current()
    return project.do("mypy", MypyTask, group="lint", **kwargs)
