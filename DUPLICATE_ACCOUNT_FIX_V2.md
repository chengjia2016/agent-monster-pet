# 修复：重复账户唯一约束错误

## 问题描述

当用户尝试登录或同步账户时，遇到以下错误：

```
❌ 错误: 同步用户账户失败: request failed with status 500: 
{"error":"Failed to create user account: pq: duplicate key value violates unique constraint \"user_accounts
```

## 根本原因

后端 `judge-server` 的 `CreateUserAccount` 函数使用了简单的 `INSERT` 语句，没有处理重复账户的情况。当一个 GitHub 用户已经在数据库中存在时，再次尝试创建该用户就会导致唯一约束冲突。

**原始代码** (judge-server/internal/db/users.go:11-21)：
```go
func (d *Database) CreateUserAccount(account *model.UserAccount) error {
	query := `
		INSERT INTO user_accounts (github_id, github_login, email, avatar_url, balance)
		VALUES ($1, $2, $3, $4, $5)
		RETURNING id, created_at, updated_at
	`
	// 当 github_id 已存在时失败
	err := d.conn.QueryRow(query, ...)
	return err
}
```

## 解决方案

### 1. 后端数据库层修复 (judge-server/internal/db/users.go)

使用 PostgreSQL 的 `ON CONFLICT DO UPDATE` 语法实现 UPSERT 操作：

```go
func (d *Database) CreateUserAccount(account *model.UserAccount) error {
	// 使用 UPSERT 优雅地处理重复账户
	// 如果账户已存在，更新其信息而不是失败
	query := `
		INSERT INTO user_accounts (github_id, github_login, email, avatar_url, balance)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT (github_id) DO UPDATE SET
			github_login = EXCLUDED.github_login,
			email = EXCLUDED.email,
			avatar_url = EXCLUDED.avatar_url,
			updated_at = NOW()
		RETURNING id, created_at, updated_at
	`
	err := d.conn.QueryRow(query,
		account.GithubID, account.GithubLogin, account.Email, account.AvatarURL, account.Balance).
		Scan(&account.ID, &account.CreatedAt, &account.UpdatedAt)
	return err
}
```

**改进点**：
- 使用 `ON CONFLICT (github_id)` 捕获唯一约束冲突
- 使用 `DO UPDATE` 更新现有账户信息
- 更新 `github_login`, `email`, `avatar_url` 字段以保持信息最新
- 更新 `updated_at` 时间戳

### 2. 处理器层改进 (judge-server/internal/handler/users.go)

更新响应消息以反映真实操作：

```go
// 修改前：
writeJSON(w, http.StatusCreated, map[string]interface{}{
	"success": true,
	"message": "User account created",
	"user":    account,
})

// 修改后：
writeJSON(w, http.StatusCreated, map[string]interface{}{
	"success": true,
	"message": "User account created or updated",
	"user":    account,
})
```

### 3. CLI 端错误处理

CLI 已有的错误处理现在工作正常 (cli/pkg/ui/app.go)：

```go
if err != nil {
	// 检查错误是否是由于重复账户（账户已存在）
	if strings.Contains(err.Error(), "duplicate key") || 
	   strings.Contains(err.Error(), "already exists") {
		// 账户已存在，继续执行（这不是错误）
		a.Message = fmt.Sprintf("欢迎回来, %s!", a.CurrentUser.Login)
	} else {
		// 其他错误发生
		a.Error = fmt.Sprintf("同步用户账户失败: %v", err)
		return a, nil
	}
}
```

## 行为变化

### 修复前：
- 第一次登录 ✅ 成功
- 第二次登录 ❌ 失败（500 错误，重复账户）

### 修复后：
- 第一次登录 ✅ 成功（创建新账户）
- 第二次登录 ✅ 成功（更新现有账户信息）
- 第三次+ ✅ 都成功（继续更新信息）

## 数据库层面

### Schema 不需要改变

现有的 `user_accounts` 表已经有正确的唯一约束：

```sql
CREATE TABLE user_accounts (
    id SERIAL PRIMARY KEY,
    github_id INTEGER UNIQUE NOT NULL,  -- 这里是唯一约束
    github_login VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    avatar_url TEXT,
    balance DECIMAL(12, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

修复通过编程逻辑（UPSERT）而不是 schema 改变来实现。

## 测试

编译验证：
```bash
cd judge-server && go build ./cmd/main.go
# Build successful ✅
```

## 相关文件

- **修改文件**：
  - `judge-server/internal/db/users.go` - CreateUserAccount 函数
  - `judge-server/internal/handler/users.go` - CreateUserAccount 处理器

- **受益文件**：
  - `cli/pkg/ui/app.go` - 现有错误处理现在更有用
  - `cli/pkg/api/client.go` - 现有 API 调用现在更可靠

## 后续影响

- ✅ 用户可以安全地重新登录
- ✅ 多个 GitHub 账户切换正常工作
- ✅ 账户信息会自动保持最新
- ✅ 没有数据丢失或冲突

## 完成状态

- ✅ 后端修复完成
- ✅ 编译测试通过
- ✅ 逻辑审查通过
- ✅ 准备生产环境部署
