# This file is dual licensed under the terms of the Apache License, Version
# 2.0, and the BSD License. See the LICENSE file in the root of this repository
# for complete details.

import pytest

from packaging import metadata, requirements
from packaging.dependency_groups import resolve_dependency_groups
from packaging.errors import ExceptionGroup


@pytest.mark.parametrize("depth", [100, 101, 10_000])
def test_metadata_collects_marker_nesting_error(depth: int) -> None:
    marker = "(" * depth + 'python_version >= "3"' + ")" * depth
    data = (
        "Metadata-Version: 2.1\nName: example\nVersion: 1.0\n"
        f"Requires-Dist: demo; {marker}\n"
    )
    if depth == 100:
        parsed = metadata.Metadata.from_email(data).requires_dist
        assert parsed is not None
        assert len(parsed) == 1
        assert parsed[0].name == "demo"
        assert parsed[0].marker is not None
        assert parsed[0].marker.evaluate({"python_version": "3.14"})
    else:
        with pytest.raises(ExceptionGroup) as exc_info:
            metadata.Metadata.from_email(data)
        (error,) = exc_info.value.exceptions
        assert isinstance(error, metadata.InvalidMetadata)
        assert error.field == "requires-dist"
        assert isinstance(error.__cause__, requirements.InvalidRequirement)
        assert "nested more than 100 levels deep" in str(error.__cause__)


@pytest.mark.parametrize("depth", [100, 101, 10_000])
def test_dependency_group_collects_marker_nesting_error(depth: int) -> None:
    marker = "(" * depth + 'python_version >= "3"' + ")" * depth
    groups = {"test": [f"demo; {marker}"]}
    if depth == 100:
        resolved = resolve_dependency_groups(groups, "test")
        assert len(resolved) == 1
        parsed = requirements.Requirement(resolved[0])
        assert parsed.name == "demo"
        assert parsed.marker is not None
        assert parsed.marker.evaluate({"python_version": "3.14"})
    else:
        with pytest.raises(ExceptionGroup) as exc_info:
            resolve_dependency_groups(groups, "test")
        (error,) = exc_info.value.exceptions
        assert isinstance(error, requirements.InvalidRequirement)
        assert "nested more than 100 levels deep" in str(error)
