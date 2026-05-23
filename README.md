# Yandex Maps Route for Home Assistant

Custom component for Yandex Maps routes tracking.

## Installation via HACS

1. Add `stastpru/YMaps-parser` as custom repository in HACS
2. Install "Yandex Maps Route"
3. Restart Home Assistant
4. Configure via UI
EOF

# Создай hacs.json
cat > hacs.json << 'EOF'
{
  "name": "Yandex Maps Route",
  "render_readme": true,
  "homeassistant": "2024.1.0"
}