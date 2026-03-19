SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__",
    ".venv", "venv", "env", "vendor", ".next", ".nuxt",
    "coverage", ".nyc_output", "target", "out", "bin", "obj",
    ".cache", "tmp", "temp", "logs", "log", "storybook-static",
    ".pytest_cache", ".mypy_cache", ".tox",
}

SKIP_EXTENSIONS = {
    # Images / media
    ".jpg", ".jpeg", ".png", ".gif", ".ico", ".bmp", ".svg", ".webp", ".tiff",
    ".mp3", ".mp4", ".avi", ".mov", ".wav", ".ogg",
    # Archives / binaries
    ".zip", ".tar", ".gz", ".rar", ".7z", ".tgz",
    ".exe", ".dll", ".so", ".dylib", ".lib", ".a", ".bin",
    # Fonts
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    # Compiled
    ".pyc", ".pyo", ".class", ".o", ".pdb",
    # Source maps & databases
    ".map", ".db", ".sqlite", ".sqlite3",
    # PDF / office docs
    ".pdf", ".docx", ".xlsx", ".pptx",
}

SKIP_FILENAMES = {
    "package-lock.json", "yarn.lock", "pipfile.lock",
    "poetry.lock", "composer.lock", "gemfile.lock",
    "cargo.lock", "go.sum", "pnpm-lock.yaml", "bun.lockb",
    ".ds_store", "thumbs.db",
}


ALLOWED_HIDDEN = {
    ".gitignore", ".env.example", ".eslintrc", ".eslintrc.json",
    ".eslintrc.js", ".prettierrc", ".prettierrc.json", ".babelrc",
    ".editorconfig", ".nvmrc", ".python-version",
}


PRIORITY_MAP = {
    "readme.md": 0, "readme.rst": 0, "readme.txt": 0, "readme": 0,
    "package.json": 1, "pyproject.toml": 1, "requirements.txt": 1,
    "setup.py": 1, "setup.cfg": 1, "cargo.toml": 1, "go.mod": 1,
    "composer.json": 1, "gemfile": 1, "pom.xml": 1, "build.gradle": 1,
    "dockerfile": 2, "docker-compose.yml": 2, "docker-compose.yaml": 2,
    ".env.example": 2, "makefile": 2, "justfile": 2,
    "main.py": 3, "app.py": 3, "index.js": 3, "index.ts": 3,
    "main.go": 3, "main.rs": 3, "app.js": 3, "server.js": 3,
    "server.py": 3, "manage.py": 3, "wsgi.py": 3, "asgi.py": 3,
}

SOURCE_EXTS = {
    ".py", ".js", ".ts", ".go", ".rs", ".java", ".rb", ".php",
    ".cs", ".cpp", ".c", ".h", ".vue", ".jsx", ".tsx", ".kt", ".swift",
    ".ex", ".exs", ".clj", ".scala", ".hs", ".ml",
}

CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"}
