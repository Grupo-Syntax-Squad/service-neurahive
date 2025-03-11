# service-neurahive

## Getting started

If you are likely going to commit to any submodule, make sure to follow their readme to install
any dev dependency and necessary runtimes. 

You must install node, if don't already have it.
```bash
sudo apt update
sudo apt upgrade

# installs nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# download and install Node.js (you may need to restart the terminal)
nvm install 20

# verifies the right Node.js version is in the environment
node -v # should print `v20.18.1`

# verifies the right npm version is in the environment
npm -v # should print `10.8.2`
```
Now you will run theses commands to set up your commit envinronment to follow our commit, version and changelog patterns.
```bash
npm ci
npx husky init
echo "npx commitlint --version" > .husky/pre-commit
echo "npx --no -- commitlint --verbose --config commitlint.config.js --edit \$1" > .husky/commit-msg
echo "export HUSKY=0
npm run changelog
export HUSKY=1" > .husky/pre-push
```

Make a copy of the `.env.example` file and rename it to `.env`
```bash
cp .env.example .env
```
Change the following variable in the `.env` file to:
```dotenv
DATABASE_URI=postgresql+asyncpg://postgres:password@localhost:5432/neurahive
```
### Setting up you development environment
Make sure `python 3.12` or newer is installed:
```bash
python3 -V
```
**If you are not:**
Install python 3.12 or later, your machine probably includes it by default but you may not have this python version installed, you can install it via apt using theses commands:
```bash
sudo apt update
sudo apt upgrade
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
```
It might be necessary to install pip as well, you may do so by running:
```bash
sudo apt install python3.12-distutils
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.12 get-pip.py
```
Now, create a virtual environment for this project and install its dependencies with:
```bash
sudo apt install python3.12-venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This file is automatically generated during deployment, but locally you still have to create it, the values you put here have do not affect how the system works.
### Installing and configuring Docker
Install Docker:
```bash
# FONTE: https://docs.docker.com/engine/install/ubuntu/
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo docker run --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -d postgres:16
```
#### Running this project with docker
Just run:
```bash
docker-compose up --build
```
*NOTE*: Do not change their specification.

### Installing and configuring DBeaver
Access the website https://dbeaver.io/download/, download and install DBeaver
- Open DBeaver (if asked to create an example database, click no)
- When opening a window to connect a database, click on PostgreSQL and Next (If it doesn't open, click on Database > new connection)
- Put the following configuration:
  - Host: localhost
  - Port: 5432
  - Database: postgres (check a opção `View all databases`)
  - Authentication: Database Native
  - Username: postgres
  - Password: password
- Click on `Test connection` (If necessary, click on Download to download the driver)
- Click `Finish`
- If it worked, you have a `postgres` database and a `public` schema

**Create a database `neurahive`**
- Right click on `database` and `create database`
- Just enter the database name `copa` and click OK
- Right click on `neurahive` and click `set as default`

### Creating and managing your database (**For future reference**)
We use alembic to manage database migrations. To start your local database versioning run this command:
```bash
source .venv/bin/activate
alembic init alembic
```

You are probably using a postgres dump as the base of your database, in that case you will need to delete all rows inside the table `alembic_version` or run the following command:
```bash
alembic stamp head --purge
```
#### Creating a migration
Alembic can programmatically create a migration for you, use this command to generate a migration:
```bash
source .venv/bin/activate
alembic revision --autogenerate -m "a basic description"
```
A description is but optional however it might prove good to maintain them so that you know the order and which certain changes happened in your local database.
Then, to *commit* them to your database run:
```bash
source .venv/bin/activate
alembic upgrade head
```

### Checking your code for lint and type errors
By installing the `tests/requirements.txt` file, you should have these 2 libraries included in your environment: **ruff** and **mypy**. To use them, simply activate your virtual environment and run:
```bash
source .venv/bin/activate
mypy .
# and
ruff check .
```

## Running tests
To run the tests you must change the following variable in `.env`:
```dotenv
DATABASE_IN_TEST_MODE=true
```
Run:
```bash
source .venv/bin/activate
pytest
```

## Developing
To run this project, just open a terminal and run:
```console
python -m gunicorn --bind 127.0.0.1:5090 --workers 2 --log-level debug --worker-class uvicorn.workers.UvicornWorker --timeout 900 main:app
```
For Visual Studio Code, you can set up a launch for easy debugging in your `.vscode/launch.json` with this:
```json
{
    "version": "0.0.0",
    "configurations": [
        {
            "name": "service-copa",
            "request": "launch",
            "type": "debugpy",
            "justMyCode": false,
            "python" : "${workspaceFolder}/service-copa/.venv/bin/python",
            "cwd": "${workspaceFolder}/service-copa",
            "module": "gunicorn",
            "args": [
                "--bind", "127.0.0.1:5090",
                "--workers", "2",
                "--log-level", "debug",
                "--worker-class", "uvicorn.workers.UvicornWorker",
                "--timeout", "900",
                "main:app"
            ],
            "console": "integratedTerminal",
            "preLaunchTask": "py-service-copa-dependencies"
        }
    ]
}
```
You will need to add this task in `.vscode/tasks.json` too:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "py-service-copa-dependencies",
            "type": "shell",
            "command": "cd ${workspaceFolder}/service-copa && source .venv/bin/activate && python -m pip install -r requirements.txt && python -m pip install -r tests/requirements.txt",
            "presentation": {
                "reveal": "silent",
                "revealProblems": "onProblem",
                "close": true
            }
        }
    ]
}
```
**Tip:** Visual Studio Code has an extension that automatically checks for lint errors using ruff, just open the extensions tab and search for *@id:charliermarsh.ruff*.
Its also possible to make VSCode automatically format your code every time you save any file with this configuration in your `.vscode/settings.json`:
```json
{
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "ruff.lint.args": ["--config", "${workspaceFolder}/service-copa/pyproject.toml"],
    "editor.rulers": [88],
    "python.testing.enabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "service-copa/tests"
    ]
}
```

## Endpoint return pattern
``` python
# app/schemas/api.py
class BasicResponse(BaseModel, Generic[T]):
    message: str = Field('', title="Mensagem", description="Mensagem de retorno")
    data: T | None = Field(None, description="Dado de retorno da API")
```
``` python
# app/routers/exemplo.py
@router.get("/{id_consulta}")
async def exemplo_get(
    id_consulta: int,
    database: AsyncSession = Depends(get_session),
) -> BasicResponse[ExemploGet]:
    return await ClasseProcessadora(id_consulta, database).consultar()
```
``` python
# app/routers/exemplo_processador_de_dados/processador_de_dados.py
class ClasseProcessadora:
    def __init__(self, _id: int, db: AsyncSession) -> None:
        self._id = _id
        self._db = db
        self._result: dict[str, Any] = {}

    async def consultar(self) -> BasicResponse[ExemploGet]:
        try:
            await self._getExemploById()
            return BasicResponse[ExemploGet](
                message="",
                data=self._result
            )
        except Exception as e:
            log_error(e, "Erro ao obter os dados")
        return BasicResponse()
    
    async def _getExemploById(self) -> None:
        exemplo = await db_model.Exemplo.get_by_id(self._db, self._id)
        if exemplo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrada"
            )
        self._result = exemplo._asdict()
```

When returning the endpoint, you must always use the `BasicResponse` model, passing the data model to be returned:
- **message** used for back-end message (Ex.: Registered successfully). The message is optional, in the GET method there is normally no message;
- **data** data to be returned;

The error generation must be `raise HTTPException`, passing the error code in `status_code` and the error message in `detail`

## Commits
When committing your code you **MUST** add one of the following tags to the start of your commit:
* fix: You fixed a bug;
* feature: You added new functionality, module or changed how another feature works;
* refactor: You reimplemented a functionality;
* docs: You added documentation to a piece of code, this readme ou changed the changelog template;
* ci: You modified in any way the file `gitlab-ci`;
* test: You added new tests, changed existing ones or update test dependencies;
* security: You added or fixed a security flaw;
* deprecated: You set a feature as deprecated; or
* remove: You removed a feature.
<br>

When you are ready to create a merge request, simply push your changes to gitlab and create a merge request from the web page. That's it.