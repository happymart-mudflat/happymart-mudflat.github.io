# 행복마트 갯벌체험장 홈페이지

- `index.html` — 홈페이지 전체 (물때 데이터 포함)
- `tools/update_tides.py` — 국립해양조사원 API로 45일치 물때를 받아 index.html을 갱신
- `.github/workflows/update-tides.yml` — 매일 새벽 4시 10분 자동 갱신

## 설정
1. 저장소 Settings → Secrets and variables → Actions → New repository secret
   이름 `KHOA_KEY`, 값: 공공데이터포털 일반 인증키
2. Settings → Pages → Branch: `main` / `(root)` → Save
3. Actions → "물때 자동 갱신" → Run workflow 로 한 번 실행해 확인
