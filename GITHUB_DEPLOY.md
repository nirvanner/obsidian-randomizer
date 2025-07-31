# 🚀 Инструкция по публикации в GitHub

## 1. Создание репозитория

1. Перейдите на [GitHub](https://github.com)
2. Нажмите "New repository"
3. Название: `obsidian-randomizer`
4. Описание: `Элегантный виджет для случайного просмотра заметок из Obsidian хранилища`
5. Выберите "Public"
6. НЕ ставьте галочки на README, .gitignore, license (у нас уже есть)
7. Нажмите "Create repository"

## 2. Загрузка файлов

```bash
# Клонируйте репозиторий
git clone https://github.com/YOUR_USERNAME/obsidian-randomizer.git
cd obsidian-randomizer

# Скопируйте все файлы из папки obs_vidg (кроме build/, dist/, __pycache__/)
# Добавьте файлы в git
git add .

# Сделайте первый коммит
git commit -m "Initial commit: Obsidian Randomizer Widget v3.0.0"

# Отправьте на GitHub
git push origin main
```

## 3. Настройка Releases

1. Перейдите в раздел "Releases"
2. Нажмите "Create a new release"
3. Tag: `v3.0.0`
4. Title: `Obsidian Randomizer v3.0.0 - Новый дизайн и настройки`
5. Описание:
```
## 🎉 Новый релиз!

### ✨ Что нового:
- 🎨 Полностью переработанный дизайн в стиле Obsidian
- ⚙️ Удобное окно настроек
- 🔧 Универсальность - работает на любом ПК
- 💾 Автосохранение настроек
- 📝 Поддержка Markdown заголовков

### 📥 Скачать:
- `obsidian_randomizer.exe` - для Windows 10/11
```

6. Загрузите файл `dist/obsidian_randomizer.exe` (если есть)
7. Нажмите "Publish release"

## 4. Обновление README

Замените в README.md:
- `your-username` → ваш GitHub username
- `your-email@example.com` → ваш email

## 5. Дополнительные настройки

### Issues и Discussions
- Включите Issues в настройках репозитория
- Включите Discussions для обсуждений

### GitHub Pages (опционально)
1. Перейдите в Settings → Pages
2. Source: "Deploy from a branch"
3. Branch: `main`
4. Folder: `/docs`
5. Создайте папку `docs` с документацией

## 6. Структура проекта

```
obsidian-randomizer/
├── obsidian_randomizer.py    # Основной код (19KB, 423 строки)
├── requirements.txt          # Зависимости
├── README.md                 # Документация
├── CHANGELOG.md             # История версий
├── LICENSE                  # MIT лицензия
└── .gitignore              # Исключения Git
```

## 7. Готово! 🎉

Ваш проект готов к использованию! Пользователи смогут:
- Скачать исходный код
- Установить зависимости: `pip install -r requirements.txt`
- Запустить: `python obsidian_randomizer.py`
- Собрать exe: `pyinstaller --onefile --windowed obsidian_randomizer.py` 