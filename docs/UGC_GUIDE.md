# Monster Designer Guide (UGC) / 怪兽设计师指南

Agent Monster now allows players to design their own monsters! Your creations can be submitted to your repository and, if voted for by the community, added to the global **Egg Pool**.

代码怪兽现在允许玩家设计自己的怪兽！您的作品可以提交到您的仓库，如果通过社区投票，将被加入全球**孵化池**。

---

## 🎨 Design Workflow / 设计流程

### 1. Create a Design / 创建设计
Use the `monster_design` tool to define your monster's attributes.
使用 `monster_design` 工具定义您的怪兽属性。

**Example Prompt:**
> *"I want to design a monster named 'Cyber Dragon', type 'Logic', with HP 80, ATK 120, DEF 60, SPD 100."*
> *"我想设计一个名为 'Cyber Dragon' 的怪兽，属性为 'Logic'，数值为：HP 80, ATK 120, DEF 60, SPD 100。"*

### 2. Prepare for Submission / 准备提交
Once you are happy with the design, move it to your repository using `monster_submit_design`.
完成设计后，使用 `monster_submit_design` 将其移动到您的仓库目录。

**Example Prompt:**
> *"Submit my design for 'Cyber Dragon'."*
> *"提交我的 'Cyber Dragon' 设计。"*

This will move the file to `/designs/monsters/cyber_dragon.soul`.

### 3. Git Push / 提交到 GitHub
Commit and push the design to your own GitHub repository.
将设计文件提交并推送到您自己的 GitHub 仓库。

```bash
git add designs/monsters/cyber_dragon.soul
git commit -m "feat: design new monster Cyber Dragon"
git push origin main
```

### 4. Voting & Integration / 投票与集成
- **Discovery**: The Judge Server periodically scans all forked repositories for new `.soul` files in the `designs/monsters/` folder.
- **Voting**: Players can visit your repo and "Vote" (e.g., via Stars or a dedicated voting issue).
- **Global Pool**: Once a design receives enough votes, it is added to the Judge Server's global registry. New eggs will then have a chance to hatch into your designed monster!

---

## 📊 Design Constraints / 设计约束

To maintain balance, the sum of base stats (HP + ATK + DEF + SPD) should be reasonable. The Judge Server will validate these before integration.
为了保持平衡，基础属性的总和应保持在合理范围内。裁判服务器在集成前会进行数值校验。

**Start creating your monster legacy today!**
**今天就开始创造您的怪兽传奇吧！**
