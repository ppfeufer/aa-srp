appname = aa-srp
package = aasrp

help:
	@echo "Makefile for $(appname)"

translationfiles:
	cd $(package) && \
	django-admin makemessages \
		-l de \
		-l es \
		-l fr_FR \
		-l it_IT \
		-l ja \
		-l ko_KR \
		-l ru \
		-l zh_Hans \
		--keep-pot \
		--ignore 'build/*'

compiletranslationfiles:
	cd $(package) && \
	django-admin compilemessages -l de  && \
	django-admin compilemessages -l es  && \
	django-admin compilemessages -l fr_FR  && \
	django-admin compilemessages -l it_IT  && \
	django-admin compilemessages -l ja  && \
	django-admin compilemessages -l ko_KR  && \
	django-admin compilemessages -l ru  && \
	django-admin compilemessages -l zh_Hans

graph_models:
	python ../myauth/manage.py graph_models $(package) --arrow-shape normal -o $(appname)-models.png

coverage:
	rm -rfv htmlcov && \
	coverage run ../myauth/manage.py test $(package) --keepdb --failfast && coverage html && coverage report -m

build_test:
	rm -rfv dist && \
	python3 -m build

tox_tests:
	export USE_MYSQL=False && \
	tox
