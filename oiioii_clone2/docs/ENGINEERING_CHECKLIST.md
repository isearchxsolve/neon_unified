# Engineering checklist (oiioii-style platform)

- [ ] Auth register/login (JWT)
- [ ] Projects CRUD
- [ ] Workflow start endpoint
- [ ] Job list/status endpoints
- [ ] Asset list endpoint
- [ ] MediaGenerationService reads keys from env only
- [ ] Workflow stages: script → character → scene → storyboard → render → sound
- [ ] Failed media calls mark job FAILED with error payload
- [ ] Frontend: project workspace + agent timeline + asset gallery
- [ ] Frontend: loading / empty / error states
- [ ] Tests for workflow service + auth
- [ ] docker-compose for api + db (+ worker if async)
