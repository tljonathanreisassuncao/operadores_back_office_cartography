#!/bin/bash

set -e

APP_NAME="ConversorCartografico"
VERSION="1.0.0"
MAIN_SCRIPT="converter_tps_gui.py"
ICON_SOURCE="img/icon.png"
ICON_NAME="icon.png"
DESKTOP_FILE="${APP_NAME}.desktop"
CONVERTER_DIR="ConvertRinex"

# 1. Limpa builds anteriores
echo "🧹 Limpando builds anteriores..."
rm -rf build dist *.deb ${APP_NAME}_${VERSION}_amd64.deb pkg deb_build

# 2. Gera o executável com PyInstaller
echo "⚙️ Gerando executável com PyInstaller..."
pyinstaller --noconfirm --onefile --windowed \
  --add-data "${ICON_SOURCE}:img" \
  "${MAIN_SCRIPT}"

# 3. Prepara estrutura para o pacote .deb
echo "📁 Criando estrutura para pacote .deb..."
mkdir -p deb_build/usr/bin
mkdir -p deb_build/usr/bin/${CONVERTER_DIR}
mkdir -p deb_build/usr/share/icons/hicolor/256x256/apps
mkdir -p deb_build/usr/share/applications

# 4. Copia binário e ícone
cp "dist/${MAIN_SCRIPT%.py}" "deb_build/usr/bin/${APP_NAME}"
cp "${ICON_SOURCE}" "deb_build/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"

echo "🧠 Copiando pasta ConvertRinex..."
cp -r "${CONVERTER_DIR}/." "deb_build/usr/bin/${CONVERTER_DIR}/"

# 5. Cria o .desktop
cat > "deb_build/usr/share/applications/${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Version=1.0
Name=Conversor Cartográfico
Comment=Ferramenta para conversão de arquivos RINEX
Exec=/usr/bin/${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Type=Application
Categories=Utility;
EOF

# 6. Cria o pacote .deb com FPM
echo "📦 Gerando pacote .deb..."
fpm -s dir -t deb -n "${APP_NAME}" -v "${VERSION}" --architecture amd64 \
    --description "Conversor de arquivos .tps para RINEX - Psyche Aerospace" \
    --deb-no-default-config-files \
    -C deb_build

echo "✅ Pacote .deb gerado com sucesso!"
