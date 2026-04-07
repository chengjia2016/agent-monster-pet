# Judge Server 部署状态

**状态**: ✅ 在线并正常运行

**访问地址**: http://agentmonster.openx.pro:10000

## 部署信息

### 运行环境
- **操作系统**: Linux (Ubuntu)
- **运行方式**: systemd service (自动重启)
- **进程名**: judge-server
- **端口**: 10000
- **数据库**: PostgreSQL (agent_monster)

### 服务命令
```bash
# 查看状态
systemctl status judge-server

# 启动/停止/重启
systemctl start judge-server
systemctl stop judge-server
systemctl restart judge-server

# 查看日志
journalctl -u judge-server -f
```

## 可用的API端点

### 健康检查
```
GET /health
```

### 用户账户管理

#### 创建用户账户
```
POST /api/users/create
Content-Type: application/json

{
  "github_id": 12345,
  "github_login": "username",
  "email": "user@example.com",
  "balance": 100.0
}

Response: 201 Created
{
  "success": true,
  "message": "User account created",
  "user": { ... }
}
```

#### 获取用户账户
```
GET /api/users/{github_id}

Response: 200 OK
{
  "id": 1,
  "github_id": 12345,
  "github_login": "username",
  "email": "user@example.com",
  "balance": 100.0,
  "created_at": "2026-04-07T14:17:42Z",
  "updated_at": "2026-04-07T14:17:42Z"
}
```

#### 获取用户余额
```
GET /api/user/balance/get?github_id={github_id}

Response: 200 OK
{
  "balance": 100.0
}
```

#### 更新用户余额
```
POST /api/user/balance/update
Content-Type: application/json

{
  "github_id": 12345,
  "amount": 50.0,
  "description": "Purchase"
}

Response: 200 OK
{
  "success": true,
  "balance": 150.0
}
```

### Pokemon 管理

#### 添加 Pokemon
```
POST /api/user/pokemons/add
Content-Type: application/json

{
  "github_id": 12345,
  "pet_id": "pet_001",
  "pet_name": "Pikachu",
  "level": 5,
  "species": "Electric"
}

Response: 201 Created
```

#### 获取用户 Pokemon 列表
```
GET /api/user/pokemons/get?github_id={github_id}

Response: 200 OK
[
  {
    "id": 1,
    "github_id": 12345,
    "pet_id": "pet_001",
    "pet_name": "Pikachu",
    "level": 5,
    "species": "Electric",
    "created_at": "2026-04-07T14:17:42Z"
  }
]
```

### 物品库存管理

#### 添加物品
```
POST /api/user/inventory/add
Content-Type: application/json

{
  "github_id": 12345,
  "item_id": "item_001",
  "item_name": "Pokeball",
  "quantity": 10
}

Response: 201 Created
```

#### 获取库存
```
GET /api/user/inventory/get?github_id={github_id}

Response: 200 OK
[
  {
    "id": 1,
    "github_id": 12345,
    "item_id": "item_001",
    "item_name": "Pokeball",
    "quantity": 10,
    "created_at": "2026-04-07T14:17:42Z",
    "updated_at": "2026-04-07T14:17:42Z"
  }
]
```

### 交易记录

#### 获取交易历史
```
GET /api/user/transactions/get?github_id={github_id}

Response: 200 OK
[
  {
    "id": 1,
    "github_id": 12345,
    "transaction_type": "balance_update",
    "amount": 50.0,
    "description": "Purchase",
    "balance_before": 100.0,
    "balance_after": 150.0,
    "created_at": "2026-04-07T14:17:42Z"
  }
]
```

## 数据库架构

### 用户相关表

**user_accounts**
- id: SERIAL PRIMARY KEY
- github_id: INTEGER UNIQUE NOT NULL
- github_login: VARCHAR(255) NOT NULL
- email: VARCHAR(255)
- avatar_url: TEXT
- balance: DECIMAL(12, 2) DEFAULT 0.0
- created_at, updated_at: TIMESTAMP

**user_pokemons**
- id: SERIAL PRIMARY KEY
- github_id: INTEGER FOREIGN KEY
- pet_id: TEXT NOT NULL UNIQUE
- pet_name: TEXT NOT NULL
- level: INTEGER DEFAULT 1
- species: TEXT
- created_at: TIMESTAMP

**user_inventory**
- id: SERIAL PRIMARY KEY
- github_id: INTEGER FOREIGN KEY
- item_id: VARCHAR(255) NOT NULL
- item_name: VARCHAR(255) NOT NULL
- quantity: INTEGER DEFAULT 1
- acquired_at: TIMESTAMP

**account_transactions**
- id: SERIAL PRIMARY KEY
- github_id: INTEGER FOREIGN KEY
- transaction_type: VARCHAR(50) NOT NULL
- amount: DECIMAL(12, 2)
- description: TEXT
- balance_before, balance_after: DECIMAL(12, 2)
- created_at: TIMESTAMP

## 配置文件

配置文件位置: `/root/pet/agent-monster-pet/judge-server/.config/config.yaml`

```yaml
server:
  host: 0.0.0.0
  port: 10000

database:
  host: localhost
  port: 5432
  user: postgres
  password: xiaodudu
  dbname: agent_monster
  sslmode: disable

settlement:
  daily_time: "00:00"
  sync_to_github: false
  sync_interval_seconds: 300
```

## 故障排查

### Judge Server 不响应
1. 检查服务状态: `systemctl status judge-server`
2. 查看日志: `journalctl -u judge-server -n 50`
3. 重启服务: `systemctl restart judge-server`

### 数据库连接错误
1. 验证 PostgreSQL 是否运行: `psql -U postgres -d agent_monster -c "SELECT 1"`
2. 检查配置中的数据库连接信息
3. 确认数据库用户和密码正确

### 用户创建失败
1. 检查 github_id 是否已存在 (unique constraint)
2. 验证请求格式是否正确

## 测试命令

```bash
# 健康检查
curl http://agentmonster.openx.pro:10000/health

# 创建用户
curl -X POST http://agentmonster.openx.pro:10000/api/users/create \
  -H "Content-Type: application/json" \
  -d '{"github_id":12345,"github_login":"user1","balance":100}'

# 获取用户
curl http://agentmonster.openx.pro:10000/api/users/12345

# 添加 Pokemon
curl -X POST http://agentmonster.openx.pro:10000/api/user/pokemons/add \
  -H "Content-Type: application/json" \
  -d '{
    "github_id": 12345,
    "pet_id": "pet_001",
    "pet_name": "Pikachu",
    "level": 5,
    "species": "Electric"
  }'
```

## MCP Server 集成

Python MCP Server 已准备好与 Judge Server 集成。相关文件:
- `judge_server_client.py` - HTTP 客户端库
- `mcp_judge_server_commands.py` - MCP 命令集

集成后，MCP Server 将通过这些 API 来管理所有用户数据。

## 部署日期

- **首次部署**: 2026-04-07
- **最后更新**: 2026-04-07
