package ugc

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// MapMetadata 存储map的元数据信息
type MapMetadata struct {
	MapID        string            `json:"map_id"`
	OwnerID      int               `json:"owner_id"`
	OwnerName    string            `json:"owner_username"`
	Title        string            `json:"title"`
	Description  string            `json:"description"`
	Version      string            `json:"version"`
	Tags         []string          `json:"tags"`
	Difficulty   string            `json:"difficulty"` // easy, medium, hard
	CreatedAt    time.Time         `json:"created_at"`
	UpdatedAt    time.Time         `json:"updated_at"`
	SourceRepo   string            `json:"source_repo"` // 来源repo URL
	SourceURL    string            `json:"source_url"`  // 在repo中的路径
	Downloads    int               `json:"downloads"`
	Rating       float64           `json:"rating"` // 1-5 stars
	Reviews      int               `json:"reviews"`
	Dependencies map[string]string `json:"dependencies"` // 其他依赖的map
}

// MapExportPackage 导出的map完整包
type MapExportPackage struct {
	Metadata  MapMetadata `json:"metadata"`
	MapData   interface{} `json:"map_data"` // 原始map数据
	License   string      `json:"license"`  // 许可证
	Authors   []string    `json:"authors"`
	Changelog string      `json:"changelog"`
}

// MapExporter 负责导出map到用户repo
type MapExporter struct {
	outputDir string
	github    *GitHubHelper
	logger    Logger
}

// NewMapExporter 创建新的map导出器
func NewMapExporter(outputDir string, github *GitHubHelper, logger Logger) *MapExporter {
	return &MapExporter{
		outputDir: outputDir,
		github:    github,
		logger:    logger,
	}
}

// ExportMap 导出map到用户仓库
// returns: 本地导出路径, repo导出路径, error
func (me *MapExporter) ExportMap(mapData interface{}, metadata MapMetadata) (string, string, error) {
	me.logger.Info("开始导出map: %s (owner: %s)", metadata.MapID, metadata.OwnerName)

	// 验证metadata
	if err := me.validateMetadata(metadata); err != nil {
		return "", "", err
	}

	// 创建导出包
	exportPackage := MapExportPackage{
		Metadata: metadata,
		MapData:  mapData,
		License:  "CC-BY-4.0", // 默认许可证
		Authors:  []string{metadata.OwnerName},
	}

	// 本地导出路径
	localPath := me.buildLocalExportPath(metadata)

	// 导出到本地文件
	if err := me.saveToLocal(localPath, exportPackage); err != nil {
		return "", "", fmt.Errorf("保存到本地失败: %w", err)
	}

	me.logger.Info("✓ Map已导出到本地: %s", localPath)

	// 推送到GitHub
	repoPath, err := me.pushToGitHub(metadata, exportPackage)
	if err != nil {
		return localPath, "", fmt.Errorf("推送到GitHub失败: %w", err)
	}

	me.logger.Info("✓ Map已推送到GitHub: %s", repoPath)

	return localPath, repoPath, nil
}

// validateMetadata 验证metadata的必要字段
func (me *MapExporter) validateMetadata(metadata MapMetadata) error {
	if metadata.MapID == "" {
		return fmt.Errorf("MapID不能为空")
	}
	if metadata.OwnerName == "" {
		return fmt.Errorf("OwnerName不能为空")
	}
	if metadata.Title == "" {
		return fmt.Errorf("Title不能为空")
	}
	if metadata.Difficulty == "" {
		metadata.Difficulty = "medium" // 默认难度
	}
	// 验证难度值
	validDifficulties := map[string]bool{"easy": true, "medium": true, "hard": true}
	if !validDifficulties[metadata.Difficulty] {
		return fmt.Errorf("无效的难度: %s (must be: easy, medium, hard)", metadata.Difficulty)
	}
	return nil
}

// buildLocalExportPath 构建本地导出路径
func (me *MapExporter) buildLocalExportPath(metadata MapMetadata) string {
	timestamp := metadata.CreatedAt.Format("20060102_150405")
	filename := fmt.Sprintf("%s_%s_%s.json",
		metadata.OwnerName,
		metadata.MapID,
		timestamp,
	)
	return filepath.Join(me.outputDir, "exports", filename)
}

// saveToLocal 保存map到本地文件
func (me *MapExporter) saveToLocal(filePath string, exportPackage MapExportPackage) error {
	// 确保目录存在
	dir := filepath.Dir(filePath)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("创建目录失败: %w", err)
	}

	// 序列化
	data, err := json.MarshalIndent(exportPackage, "", "  ")
	if err != nil {
		return fmt.Errorf("JSON序列化失败: %w", err)
	}

	// 写入文件
	if err := os.WriteFile(filePath, data, 0644); err != nil {
		return fmt.Errorf("写入文件失败: %w", err)
	}

	return nil
}

// pushToGitHub 推送map到用户的GitHub仓库
func (me *MapExporter) pushToGitHub(metadata MapMetadata, exportPackage MapExportPackage) (string, error) {
	if me.github == nil {
		return "", fmt.Errorf("GitHub helper未初始化")
	}

	// 构建repo路径
	// maps/<owner>/<map_id>/map.json
	repoDirPath := fmt.Sprintf("maps/%s", metadata.MapID)
	repoFilePath := filepath.Join(repoDirPath, "map.json")
	metadataPath := filepath.Join(repoDirPath, "metadata.json")
	readmePath := filepath.Join(repoDirPath, "README.md")

	// 序列化数据
	mapDataJSON, err := json.MarshalIndent(exportPackage.MapData, "", "  ")
	if err != nil {
		return "", fmt.Errorf("Map数据序列化失败: %w", err)
	}

	metadataJSON, err := json.MarshalIndent(exportPackage.Metadata, "", "  ")
	if err != nil {
		return "", fmt.Errorf("Metadata序列化失败: %w", err)
	}

	readmeContent := me.generateReadmeContent(metadata)

	// 推送文件到GitHub
	files := map[string]string{
		repoFilePath: string(mapDataJSON),
		metadataPath: string(metadataJSON),
		readmePath:   readmeContent,
	}

	if err := me.github.PushFilesToRepo(files); err != nil {
		return "", fmt.Errorf("推送文件失败: %w", err)
	}

	repoPath := fmt.Sprintf("maps/%s", metadata.MapID)
	return repoPath, nil
}

// generateReadmeContent 生成README内容
func (me *MapExporter) generateReadmeContent(metadata MapMetadata) string {
	readme := fmt.Sprintf(`# %s

**作者**: %s  
**Map ID**: %s  
**难度**: %s  
**创建时间**: %s  

## 描述

%s

## 特性

- 大小: %dx%d
- 难度级别: %s
- 标签: %s

## 来源

- 来自: %s
- 原始URL: %s

---

**许可证**: CC-BY-4.0  
**版本**: %s
`,
		metadata.Title,
		metadata.OwnerName,
		metadata.MapID,
		metadata.Difficulty,
		metadata.CreatedAt.Format("2006-01-02 15:04:05"),
		metadata.Description,
		metadata.SourceRepo,
		metadata.SourceRepo,
		metadata.Difficulty,
		fmt.Sprintf("%v", metadata.Tags),
		metadata.OwnerName,
		metadata.SourceURL,
		metadata.Version,
	)
	return readme
}

// ListExportedMaps 列出所有导出的map
func (me *MapExporter) ListExportedMaps() ([]string, error) {
	exportsDir := filepath.Join(me.outputDir, "exports")

	entries, err := os.ReadDir(exportsDir)
	if err != nil {
		if os.IsNotExist(err) {
			return []string{}, nil
		}
		return nil, err
	}

	var maps []string
	for _, entry := range entries {
		if !entry.IsDir() && filepath.Ext(entry.Name()) == ".json" {
			maps = append(maps, entry.Name())
		}
	}

	return maps, nil
}

// GetExportedMapMetadata 获取已导出map的元数据
func (me *MapExporter) GetExportedMapMetadata(filename string) (*MapMetadata, error) {
	filePath := filepath.Join(me.outputDir, "exports", filename)

	data, err := os.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("读取文件失败: %w", err)
	}

	var exportPackage MapExportPackage
	if err := json.Unmarshal(data, &exportPackage); err != nil {
		return nil, fmt.Errorf("JSON反序列化失败: %w", err)
	}

	return &exportPackage.Metadata, nil
}
