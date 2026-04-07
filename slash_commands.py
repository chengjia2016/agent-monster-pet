#!/usr/bin/env python3
"""
Agent Monster Slash Command System for OpenCode
Provides intelligent /monster commands with auto-completion
"""

import json
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict


class CommandCategory(Enum):
    """命令分类"""
    MENU = "menu"
    USER = "user"
    SHOP = "shop"
    ACCOUNT = "account"
    INVENTORY = "inventory"
    HELP = "help"


@dataclass
class CommandParam:
    """命令参数定义"""
    name: str
    description: str
    type: str  # "string", "number", "enum", etc.
    required: bool = True
    default: Optional[str] = None
    enum_values: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class SlashCommand:
    """斜杠命令定义"""
    name: str
    description: str
    category: CommandCategory
    usage: str  # 使用示例
    params: List[CommandParam]
    long_description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "usage": self.usage,
            "long_description": self.long_description,
            "params": [p.to_dict() for p in self.params]
        }


class SlashCommandRegistry:
    """斜杠命令注册表"""
    
    def __init__(self):
        self.commands: Dict[str, SlashCommand] = {}
        self._register_commands()
    
    def _register_commands(self):
        """注册所有可用命令"""
        
        # ====== 快速启动命令 ======
        self.register(SlashCommand(
            name="start",
            description="快速启动游戏 (自动从 GitHub CLI 获取用户名)",
            category=CommandCategory.MENU,
            usage="/monster start",
            long_description="使用最简单的方式启动游戏。自动从 gh CLI 获取你的 GitHub 用户名，无需手动输入。",
            params=[]
        ))
        
        # ====== 菜单命令 ======
        self.register(SlashCommand(
            name="menu",
            description="启动交互式游戏菜单",
            category=CommandCategory.MENU,
            usage="/monster menu username:your_username",
            long_description="启动交互式菜单系统，使用数字选择操作。初始化用户账户并显示主菜单。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        self.register(SlashCommand(
            name="menu account",
            description="查看账户信息菜单",
            category=CommandCategory.ACCOUNT,
            usage="/monster menu account username:your_username",
            long_description="显示账户菜单，包含用户资料、余额、交易统计等信息。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        self.register(SlashCommand(
            name="menu shop",
            description="进入商店菜单",
            category=CommandCategory.SHOP,
            usage="/monster menu shop username:your_username",
            long_description="显示商店菜单，浏览所有可购买的物品及价格。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        self.register(SlashCommand(
            name="menu inventory",
            description="查看背包菜单",
            category=CommandCategory.INVENTORY,
            usage="/monster menu inventory username:your_username",
            long_description="显示你拥有的所有物品及数量。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        self.register(SlashCommand(
            name="menu help",
            description="显示帮助菜单",
            category=CommandCategory.HELP,
            usage="/monster menu help",
            long_description="显示游戏指南和帮助信息。",
            params=[]
        ))
        
        self.register(SlashCommand(
            name="select",
            description="在菜单中选择选项",
            category=CommandCategory.MENU,
            usage="/monster select username:your_username option:1",
            long_description="在当前菜单中选择一个选项（0-9）。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                ),
                CommandParam(
                    name="option",
                    description="选择的选项编号",
                    type="enum",
                    required=True,
                    enum_values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                )
            ]
        ))
        
        # ====== 用户命令 ======
        self.register(SlashCommand(
            name="register",
            description="注册新用户账户",
            category=CommandCategory.USER,
            usage="/monster register username:your_username",
            long_description="使用GitHub用户名自动注册新账户，初始获得100精灵币和启动物品。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        self.register(SlashCommand(
            name="profile",
            description="查看用户资料",
            category=CommandCategory.USER,
            usage="/monster profile username:your_username",
            long_description="显示用户的基本信息、加入时间、最后登入时间等。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        # ====== 商店命令 ======
        self.register(SlashCommand(
            name="shop list",
            description="列出所有商品",
            category=CommandCategory.SHOP,
            usage="/monster shop list",
            long_description="显示商店中所有可购买的物品、价格和库存。",
            params=[]
        ))
        
        self.register(SlashCommand(
            name="shop buy",
            description="购买物品",
            category=CommandCategory.SHOP,
            usage="/monster shop buy username:your_username item:pokeball quantity:1",
            long_description="从商店购买指定物品。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                ),
                CommandParam(
                    name="item",
                    description="物品ID",
                    type="enum",
                    required=True,
                    enum_values=["pokeball", "ultraball", "seed_grass", "seed_water", "potion_small", "revive", "boost"]
                ),
                CommandParam(
                    name="quantity",
                    description="购买数量",
                    type="number",
                    required=False,
                    default="1"
                )
            ]
        ))
        
        # ====== 账户命令 ======
        self.register(SlashCommand(
            name="balance",
            description="查看账户余额",
            category=CommandCategory.ACCOUNT,
            usage="/monster balance username:your_username",
            long_description="显示你的精灵币余额。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        self.register(SlashCommand(
            name="stats",
            description="查看账户统计",
            category=CommandCategory.ACCOUNT,
            usage="/monster stats username:your_username",
            long_description="显示账户统计信息：总收入、总支出、交易次数、最近交易等。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        # ====== 物品命令 ======
        self.register(SlashCommand(
            name="inventory",
            description="查看背包物品",
            category=CommandCategory.INVENTORY,
            usage="/monster inventory username:your_username",
            long_description="显示你拥有的所有物品及数量。",
            params=[
                CommandParam(
                    name="username",
                    description="你的GitHub用户名",
                    type="string",
                    required=True
                )
            ]
        ))
        
        # ====== 帮助命令 ======
        self.register(SlashCommand(
            name="help",
            description="显示帮助信息",
            category=CommandCategory.HELP,
            usage="/monster help",
            long_description="显示所有可用命令和游戏指南。",
            params=[]
        ))
        
        self.register(SlashCommand(
            name="guide",
            description="显示新手指南",
            category=CommandCategory.HELP,
            usage="/monster guide",
            long_description="显示游戏新手指南，包括基本玩法、经济系统、物品等。",
            params=[]
        ))
    
    def register(self, command: SlashCommand):
        """注册命令"""
        self.commands[command.name] = command
    
    def get_command(self, name: str) -> Optional[SlashCommand]:
        """获取命令"""
        return self.commands.get(name)
    
    def get_all_commands(self) -> List[SlashCommand]:
        """获取所有命令"""
        return list(self.commands.values())
    
    def get_commands_by_category(self, category: CommandCategory) -> List[SlashCommand]:
        """按分类获取命令"""
        return [cmd for cmd in self.commands.values() if cmd.category == category]
    
    def search_commands(self, query: str) -> List[SlashCommand]:
        """搜索命令"""
        query = query.lower()
        results = []
        for cmd in self.commands.values():
            if query in cmd.name.lower() or query in cmd.description.lower():
                results.append(cmd)
        return results
    
    def get_command_completions(self, prefix: str) -> List[Dict[str, str]]:
        """获取命令自动完成建议"""
        prefix = prefix.lower()
        completions = []
        
        for cmd in self.commands.values():
            if cmd.name.lower().startswith(prefix):
                completions.append({
                    "label": cmd.name,
                    "detail": cmd.description,
                    "documentation": cmd.long_description or cmd.description
                })
        
        return sorted(completions, key=lambda x: x["label"])
    
    def to_json(self) -> str:
        """导出为JSON"""
        commands = [cmd.to_dict() for cmd in self.commands.values()]
        return json.dumps(commands, indent=2, ensure_ascii=False)
    
    def export_for_mcp(self) -> Dict[str, Any]:
        """为MCP导出命令信息"""
        by_category = {}
        for category in CommandCategory:
            cmds = self.get_commands_by_category(category)
            by_category[category.value] = [cmd.to_dict() for cmd in cmds]
        
        return {
            "total_commands": len(self.commands),
            "categories": list(CommandCategory.__members__.keys()),
            "commands_by_category": by_category,
            "all_commands": [cmd.to_dict() for cmd in self.commands.values()]
        }


def format_command_help(command: SlashCommand) -> str:
    """格式化命令帮助信息"""
    help_text = f"""
╔════════════════════════════════════════════╗
║  🎮 {command.name.upper()}
╚════════════════════════════════════════════╝

📝 描述:
  {command.description}

📚 详细说明:
  {command.long_description or command.description}

📌 用法:
  {command.usage}

⚙️  参数:
"""
    
    if command.params:
        for param in command.params:
            required = "必需" if param.required else "可选"
            help_text += f"\n  • {param.name} ({param.type}) - [{required}]\n"
            help_text += f"    {param.description}\n"
            if param.enum_values:
                help_text += f"    可用值: {', '.join(param.enum_values)}\n"
    else:
        help_text += "\n  无参数\n"
    
    help_text += f"\n📋 分类: {command.category.value}\n"
    
    return help_text


def format_commands_list() -> str:
    """格式化命令列表"""
    registry = SlashCommandRegistry()
    
    output = """
╔════════════════════════════════════════════╗
║  🎮 Agent Monster 斜杠命令列表
╚════════════════════════════════════════════╝

"""
    
    for category in CommandCategory:
        commands = registry.get_commands_by_category(category)
        if commands:
            output += f"\n📂 {category.value.upper()} 命令:\n"
            output += "─" * 44 + "\n"
            for cmd in commands:
                output += f"  /{cmd.name:<30} {cmd.description}\n"
            output += "\n"
    
     output += """
💡 使用方法:
  最简单: /monster                    - 一步启动（自动获取 GitHub 用户）
  
  或者:   /monster menu username:you  - 需要输入 GitHub 用户名
         /monster help               - 查看完整帮助

💙 前置要求:
  - 已安装 GitHub CLI (gh auth login)
  - 已在 .claude/settings.json 配置 MCP 服务器

📚 获取帮助:
  /monster help [命令名]  - 查看特定命令的详细帮助
  /monster help           - 查看所有可用命令
"""
     
     return output


if __name__ == "__main__":
    registry = SlashCommandRegistry()
    
    # 测试自动完成
    print("自动完成测试:")
    print(f"  /menu -> {registry.get_command_completions('menu')}")
    print(f"  /shop -> {registry.get_command_completions('shop')}")
    print(f"  /acc -> {registry.get_command_completions('acc')}")
    
    # 测试帮助
    print("\n\n命令帮助:")
    cmd = registry.get_command("menu")
    if cmd:
        print(format_command_help(cmd))
