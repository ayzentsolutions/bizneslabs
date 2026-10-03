import pytest
from app.tools.base import AuthorizedTool,ToolContext

class DemoTool(AuthorizedTool):
    name="demo"
    description="demo"
    async def execute(self,context,arguments): return {}

def test_tool_argument_limits():
    DemoTool().validate({"a":"ok"})
    with pytest.raises(ValueError):
        DemoTool().validate({"a":"x"*2001})
