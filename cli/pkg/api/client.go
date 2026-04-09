package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// Client 与judge-server通信的HTTP客户端
type Client struct {
	BaseURL string
	Client  *http.Client
}

// NewClient 创建新的API客户端
func NewClient(baseURL string) *Client {
	return &Client{
		BaseURL: baseURL,
		Client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

// Request 发送HTTP请求的通用方法
func (c *Client) Request(method, endpoint string, body interface{}) ([]byte, error) {
	url := c.BaseURL + endpoint

	var reqBody io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonBody)
	}

	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// RequestWithQuery 发送带查询参数的HTTP请求
func (c *Client) RequestWithQuery(method, endpoint string, query map[string]string, body interface{}) ([]byte, error) {
	url := c.BaseURL + endpoint

	// Add query parameters if provided
	if len(query) > 0 {
		values := make([]string, 0, len(query))
		for k, v := range query {
			values = append(values, fmt.Sprintf("%s=%s", k, v))
		}
		if len(values) > 0 {
			url = url + "?" + strings.Join(values, "&")
		}
	}

	var reqBody io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, fmt.Errorf("failed to marshal request body: %w", err)
		}
		reqBody = bytes.NewBuffer(jsonBody)
	}

	req, err := http.NewRequest(method, url, reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("request failed with status %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// GetBattles 获取战斗列表
func (c *Client) GetBattles() ([]Battle, error) {
	data, err := c.Request("GET", "/api/battles", nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var battles []Battle
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &battles)
	}

	return battles, nil
}

// StartBattle 开始新战斗
func (c *Client) StartBattle(attackerID, defenderID, attackerTeamID, defenderTeamID string) (map[string]interface{}, error) {
	payload := map[string]string{
		"attacker_id":      attackerID,
		"defender_id":      defenderID,
		"attacker_team_id": attackerTeamID,
		"defender_team_id": defenderTeamID,
	}

	data, err := c.Request("POST", "/api/battles/start", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	return response, nil
}

// GetBattleStatus 获取战斗状态
func (c *Client) GetBattleStatus(battleID string) (map[string]interface{}, error) {
	data, err := c.Request("GET", "/api/battles/"+battleID, nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	return response, nil
}

// GetBase 获取防守基地信息
func (c *Client) GetBase() (map[string]interface{}, error) {
	data, err := c.Request("GET", "/api/defense/base", nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	if base, ok := response["base"].(map[string]interface{}); ok {
		return base, nil
	}

	return map[string]interface{}{}, nil
}

// CreateBase 创建防守基地
func (c *Client) CreateBase(repositoryURL string) (map[string]interface{}, error) {
	payload := map[string]string{
		"repository_url": repositoryURL,
	}

	data, err := c.Request("POST", "/api/defense/base", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	if base, ok := response["base"].(map[string]interface{}); ok {
		return base, nil
	}

	return map[string]interface{}{}, nil
}

// GetPokemon 获取用户宠物列表
func (c *Client) GetPokemon() ([]Pokemon, error) {
	data, err := c.Request("GET", "/api/pokemon", nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var pokemons []Pokemon
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &pokemons)
	}

	return pokemons, nil
}

// ListWildPokemon 获取野生精灵列表
func (c *Client) ListWildPokemon() ([]WildPokemon, error) {
	data, err := c.Request("GET", "/api/wild-pokemon", nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var pokemons []WildPokemon
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &pokemons)
	}

	return pokemons, nil
}

// CapturePokemon 捕获野生精灵
func (c *Client) CapturePokemon(wildPokemonID string) (map[string]interface{}, error) {
	payload := map[string]string{
		"wild_pokemon_id": wildPokemonID,
	}

	data, err := c.Request("POST", "/api/wild-pokemon/capture", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	return response, nil
}

// GetUserPokemons 获取用户的宠物列表（从judge-server）
func (c *Client) GetUserPokemons(githubID int) ([]Pokemon, error) {
	query := map[string]string{
		"github_id": fmt.Sprintf("%d", githubID),
	}

	data, err := c.RequestWithQuery("GET", "/api/user/pokemons/get", query, nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var pokemons []Pokemon
	if pokemonsRaw, ok := response["pokemons"]; ok && pokemonsRaw != nil {
		jsonData, _ := json.Marshal(pokemonsRaw)
		json.Unmarshal(jsonData, &pokemons)
	}

	return pokemons, nil
}

// CreateOrGetUserAccount 创建或获取用户账户
func (c *Client) CreateOrGetUserAccount(githubID int, githubUsername string) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"github_id":       githubID,
		"github_username": githubUsername,
	}

	data, err := c.Request("POST", "/api/users/create", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	return response, nil
}

// GetMapByID 获取指定ID的地图
func (c *Client) GetMapByID(mapID string) (*MapData, error) {
	data, err := c.Request("GET", "/api/maps/"+mapID, nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var mapData *MapData
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &mapData)
	}

	return mapData, nil
}

// ListMaps 获取地图列表
func (c *Client) ListMaps(page, limit int) ([]MapData, error) {
	query := map[string]string{
		"page":  fmt.Sprintf("%d", page),
		"limit": fmt.Sprintf("%d", limit),
	}

	data, err := c.RequestWithQuery("GET", "/api/maps", query, nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var maps []MapData
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &maps)
	}

	return maps, nil
}

// SearchMaps 搜索地图
func (c *Client) SearchMaps(query string, page, limit int) ([]MapData, error) {
	params := map[string]string{
		"query": query,
		"page":  fmt.Sprintf("%d", page),
		"limit": fmt.Sprintf("%d", limit),
	}

	data, err := c.RequestWithQuery("GET", "/api/maps/search", params, nil)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var maps []MapData
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &maps)
	}

	return maps, nil
}

// GenerateMap 生成新地图
func (c *Client) GenerateMap(ownerID int, ownerName, mapID string, width, height int) (*MapData, error) {
	payload := map[string]interface{}{
		"owner_id":   ownerID,
		"owner_name": ownerName,
		"map_id":     mapID,
		"width":      width,
		"height":     height,
	}

	data, err := c.Request("POST", "/api/maps/generate", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var mapData *MapData
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &mapData)
	}

	return mapData, nil
}

// TraverseMap 遍历到相邻地图
func (c *Client) TraverseMap(currentMapID, direction string) (*MapData, error) {
	payload := map[string]string{
		"current_map_id": currentMapID,
		"direction":      direction,
	}

	data, err := c.Request("POST", "/api/maps/traverse", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	var mapData *MapData
	if dataRaw, ok := response["data"]; ok {
		jsonData, _ := json.Marshal(dataRaw)
		json.Unmarshal(jsonData, &mapData)
	}

	return mapData, nil
}

// ClaimStarterPokemons claims starter pokemons for a user during onboarding
func (c *Client) ClaimStarterPokemons(githubID int) (map[string]interface{}, error) {
	payload := map[string]interface{}{
		"github_id": githubID,
	}

	data, err := c.Request("POST", "/api/user/claim-starter-pokemons", payload)
	if err != nil {
		return nil, err
	}

	var response map[string]interface{}
	if err := json.Unmarshal(data, &response); err != nil {
		return nil, err
	}

	return response, nil
}
