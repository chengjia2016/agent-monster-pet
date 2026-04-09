package main

import (
	"agent-monster-cli/pkg/github"
	"agent-monster-cli/pkg/ui"
	"fmt"
)

func main() {
	accounts, _ := github.GetAuthAccounts()
	
	app := &ui.App{
		CurrentScreen: ui.AccountSelectScreen,
		AccountSelectState: &ui.AccountSelectState{
			Accounts: accounts,
			SelectedIndex: 0,
		},
	}
	
	fmt.Println(app.View())
}
