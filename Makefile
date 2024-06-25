# Makefile for AA SRP

# Variables
appname = aa-srp
appname_verbose = AA SRP
package = aasrp

# Default goal
.DEFAULT_GOAL := help

# Graph models
.PHONY: graph_models
graph_models:
	@echo "Creating a graph of the models"
	@python ../myauth/manage.py \
		graph_models \
		$(package) \
		--arrow-shape normal \
		-o $(appname)-models.png

# Help
.PHONY: help
help::
	@echo ""
	@echo "$(TEXT_BOLD)$(appname_verbose)$(TEXT_BOLD_END) Makefile"
	@echo ""
	@echo "$(TEXT_BOLD)Usage:$(TEXT_BOLD_END)"
	@echo "  make [command]"
	@echo ""
	@echo "$(TEXT_BOLD)Commands:$(TEXT_BOLD_END)"
	@echo "  $(TEXT_UNDERLINE)General:$(TEXT_UNDERLINE_END)"
	@echo "    graph_models              Create a graph of the models"
	@echo "    help                      Show this help message"
	@echo ""

# Include the configurations
include .make/conf.d/*.mk
