package ugc

import (
	"fmt"
)

// ValidationResult 验证结果
type ValidationResult struct {
	IsValid  bool
	Errors   []string
	Warnings []string
	Score    int // 0-100
}

// MapValidator 验证map的格式和平衡性
type MapValidator struct {
	logger Logger
}

func NewMapValidator(logger Logger) *MapValidator {
	return &MapValidator{
		logger: logger,
	}
}

// ValidateMap 验证map的完整性和平衡性
func (mv *MapValidator) ValidateMap(mapData interface{}, metadata MapMetadata) *ValidationResult {
	result := &ValidationResult{
		IsValid:  true,
		Errors:   []string{},
		Warnings: []string{},
		Score:    100,
	}

	// 验证元数据
	if err := mv.validateMapMetadata(metadata); err != nil {
		result.Errors = append(result.Errors, err.Error())
		result.IsValid = false
		result.Score -= 20
	}

	// 验证map数据结构
	if mapErr := mv.validateMapStructure(mapData); len(mapErr) > 0 {
		result.Errors = append(result.Errors, mapErr...)
		result.IsValid = false
		result.Score -= 30
	}

	// 检查map平衡性
	if balanceWarnings := mv.validateMapBalance(mapData); len(balanceWarnings) > 0 {
		result.Warnings = append(result.Warnings, balanceWarnings...)
		result.Score -= 10
	}

	// 检查多样性
	if diversityWarnings := mv.validateDiversity(mapData); len(diversityWarnings) > 0 {
		result.Warnings = append(result.Warnings, diversityWarnings...)
		result.Score -= 5
	}

	if result.Score < 0 {
		result.Score = 0
	}

	result.IsValid = len(result.Errors) == 0
	return result
}

// validateMapMetadata 验证map元数据
func (mv *MapValidator) validateMapMetadata(metadata MapMetadata) error {
	if metadata.MapID == "" {
		return fmt.Errorf("MapID不能为空")
	}
	if metadata.OwnerName == "" {
		return fmt.Errorf("OwnerName不能为空")
	}
	if metadata.Title == "" {
		return fmt.Errorf("标题不能为空")
	}
	if len(metadata.Title) > 100 {
		return fmt.Errorf("标题过长(最多100字符)")
	}
	if len(metadata.Description) > 1000 {
		return fmt.Errorf("描述过长(最多1000字符)")
	}
	return nil
}

// validateMapStructure 验证map数据结构
func (mv *MapValidator) validateMapStructure(mapData interface{}) []string {
	errors := []string{}

	// 类型断言检查
	mapDict, ok := mapData.(map[string]interface{})
	if !ok {
		errors = append(errors, "Map数据必须是JSON对象")
		return errors
	}

	// 检查必要字段
	requiredFields := []string{"version", "map_id", "terrain", "elements", "statistics"}
	for _, field := range requiredFields {
		if _, exists := mapDict[field]; !exists {
			errors = append(errors, fmt.Sprintf("缺少必要字段: %s", field))
		}
	}

	// 验证terrain
	if terrain, ok := mapDict["terrain"].([]interface{}); ok {
		if len(terrain) < 10 {
			errors = append(errors, "Map太小(最少10x10)")
		}
		if len(terrain) > 100 {
			errors = append(errors, "Map太大(最大100x100)")
		}
	} else {
		errors = append(errors, "terrain必须是二维数组")
	}

	// 验证elements
	if elements, ok := mapDict["elements"].([]interface{}); ok {
		if len(elements) < 5 {
			errors = append(errors, "元素过少(至少需要5个)")
		}
		if len(elements) > 200 {
			errors = append(errors, "元素过多(最多200个)")
		}
	} else {
		errors = append(errors, "elements必须是数组")
	}

	return errors
}

// validateMapBalance 验证map平衡性
func (mv *MapValidator) validateMapBalance(mapData interface{}) []string {
	warnings := []string{}

	mapDict, ok := mapData.(map[string]interface{})
	if !ok {
		return warnings
	}

	// 获取elements
	elements, ok := mapDict["elements"].([]interface{})
	if !ok {
		return warnings
	}

	// 统计元素类型
	elementCount := map[string]int{
		"wild_pokemon": 0,
		"food":         0,
		"obstacle":     0,
		"npc":          0,
	}

	for _, elem := range elements {
		if elemDict, ok := elem.(map[string]interface{}); ok {
			if elemType, ok := elemDict["type"].(string); ok {
				elementCount[elemType]++
			}
		}
	}

	// 检查平衡性
	totalElements := len(elements)

	// 野生Pokemon应该占30-50%
	pokemonPercent := (elementCount["wild_pokemon"] * 100) / totalElements
	if pokemonPercent < 30 || pokemonPercent > 50 {
		warnings = append(warnings, fmt.Sprintf(
			"野生Pokemon数量不平衡 (%.0f%%, 建议30-50%%)",
			float64(pokemonPercent),
		))
	}

	// 食物应该占20-30%
	foodPercent := (elementCount["food"] * 100) / totalElements
	if foodPercent < 20 || foodPercent > 30 {
		warnings = append(warnings, fmt.Sprintf(
			"食物数量不平衡 (%.0f%%, 建议20-30%%)",
			float64(foodPercent),
		))
	}

	// 障碍物应该占15-25%
	obstaclePercent := (elementCount["obstacle"] * 100) / totalElements
	if obstaclePercent < 15 || obstaclePercent > 25 {
		warnings = append(warnings, fmt.Sprintf(
			"障碍物数量不平衡 (%.0f%%, 建议15-25%%)",
			float64(obstaclePercent),
		))
	}

	return warnings
}

// validateDiversity 验证内容多样性
func (mv *MapValidator) validateDiversity(mapData interface{}) []string {
	warnings := []string{}

	mapDict, ok := mapData.(map[string]interface{})
	if !ok {
		return warnings
	}

	// 获取elements
	elements, ok := mapDict["elements"].([]interface{})
	if !ok {
		return warnings
	}

	// 统计不同Pokemon类型
	pokemonTypes := make(map[string]int)
	foodTypes := make(map[string]int)

	for _, elem := range elements {
		if elemDict, ok := elem.(map[string]interface{}); ok {
			if elemType, ok := elemDict["type"].(string); ok {
				if elemType == "wild_pokemon" {
					if data, ok := elemDict["data"].(map[string]interface{}); ok {
						if pokemonID, ok := data["pokemon_id"].(string); ok {
							pokemonTypes[pokemonID]++
						}
					}
				} else if elemType == "food" {
					if data, ok := elemDict["data"].(map[string]interface{}); ok {
						if foodType, ok := data["food_type"].(string); ok {
							foodTypes[foodType]++
						}
					}
				}
			}
		}
	}

	// 检查多样性 - 至少3种不同的Pokemon
	if len(pokemonTypes) < 3 {
		warnings = append(warnings, fmt.Sprintf(
			"Pokemon类型过少 (只有%d种, 建议至少3种)",
			len(pokemonTypes),
		))
	}

	// 检查多样性 - 至少2种不同的食物
	if len(foodTypes) < 2 {
		warnings = append(warnings, fmt.Sprintf(
			"食物类型过少 (只有%d种, 建议至少2种)",
			len(foodTypes),
		))
	}

	return warnings
}

// PrintResult 打印验证结果
func (mv *MapValidator) PrintResult(result *ValidationResult) {
	fmt.Println("\n╔════════════════════════════════════╗")
	fmt.Println("║         Map验证结果              ║")
	fmt.Println("╚════════════════════════════════════╝")

	if result.IsValid {
		fmt.Printf("\n✅ 验证成功! 评分: %d/100\n", result.Score)
	} else {
		fmt.Printf("\n❌ 验证失败! 评分: %d/100\n", result.Score)
	}

	if len(result.Errors) > 0 {
		fmt.Println("\n❌ 错误:")
		for i, err := range result.Errors {
			fmt.Printf("  %d. %s\n", i+1, err)
		}
	}

	if len(result.Warnings) > 0 {
		fmt.Println("\n⚠️  警告:")
		for i, warn := range result.Warnings {
			fmt.Printf("  %d. %s\n", i+1, warn)
		}
	}

	if result.IsValid && len(result.Warnings) == 0 {
		fmt.Println("\n🎉 完美! 你的Map质量非常好!")
	}
}
