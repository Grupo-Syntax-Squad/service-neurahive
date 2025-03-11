# service-neurahive


# frontend-copa

## Getting started

On this project you need to have already installed **Node.js** to start the project, if you don't have it installed, keep following the instructions

### Installing Node.js and NVM (Node Version Manager)

```bash
# installs nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# download and install Node.js (you may need to restart the terminal)
nvm install 22

# verifies the right Node.js version is in the environment
node -v
# should print `v22.11.0`

# verifies the right npm version is in the environment
npm -v
# should print `10.9.0`
```

Then install on the project folder all dependencies:

```bash
npm ci && npm start
```

And lastly change the default behavior of husky so that you can actually make a commit:

```bash
echo "npx commitlint --version" > .husky/pre-commit
```

**Everything should be good to go**, but, for future reference, you can configure your environment with the following commands:

```bash
npm ci
npx husky init
echo "npx commitlint --version" > .husky/pre-commit
echo "npx --no -- commitlint --verbose --config commitlint.config.js --edit \$1" > .husky/commit-msg
echo "export HUSKY=0
npm run changelog
export HUSKY=1" > .husky/pre-push
```

## Start Front-end React

First of all create a `vite.config.ts` on the root folder like this:
```javascript
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tsconfigPaths from "vite-tsconfig-paths"
import { fileURLToPath } from "node:url"

function devFilesPathToExclude() {
    const filesPath = ["src/dev/*"]
    return filesPath.map((src) => {
        return fileURLToPath(new URL(src, import.meta.url))
    })
}

// https://vite.dev/config/
export default defineConfig({
    define: {
        "process.env": process.env,
    },
    plugins: [react(), tsconfigPaths()],
    envPrefix: "COPA_",
    build: {
        outDir: "dist",
        chunkSizeWarningLimit: 400,
        sourcemap: false,
        rollupOptions: {
            external: [...devFilesPathToExclude()],
            output: {
                manualChunks(id) {
                    if (id.includes("/src/pages/")) {
                        const route = id.match(/\/src\/pages\/(\w+)/)
                        if (route && route[1]) {
                            return `page-${route[1]}`
                        }
                    }

                    if (id.includes("bootstrap")) {
                        return "bootstrap"
                    }
                },
            },
        },
    },
})

```

Make a copy of the `.env.example` file and rename it to `.env`
```bash
cp .env.example .env
```
Lastly, create a new file called `version.json` in your root folder with this content:
```json
{"version": "v1.0.0", "date": "2025-01-01"}
```
To run this project, manually just open a terminal and run:

```bash
npm ci && npm start
```

> Note: By default the front-end port will be `5173`

For Visual Studio Code, you can set up a launch to start and debug the application using these launchs on `.vscode/launch.json`

```json
{
    "configurations": [
        {
            "name": "Start Front-end",
            "type": "node",
            "request": "launch",
            "cwd": "${workspaceFolder}",
            "runtimeExecutable": "npm",
            "runtimeArgs": ["start"],
            "console": "internalConsole",
            "preLaunchTask": "frontend-dependencies"
        },
        {
            "name": "Debug Front-end",
            "type": "chrome",
            "request": "launch",
            "url": "http://localhost:5173",
            "webRoot": "${workspaceFolder}",
            "preLaunchTask": "waiting-frontend-start"
        }
    ],
    "compounds": [
        {
            "name": "Start and Debug Front-end",
            "configurations": ["Start Front-end", "Debug Front-end"],
            "stopAll": true
        }
    ]
}
```

> Note: With **compounds** you can start both launchs (_Start Front-end + Debug Front-end_) on the same time

You need to add also `preLaunchTask` named `frontend-dependencies` and `waiting-frontend-start` on `.vscode/tasks.json`

```json
{
    "tasks": [
        {
            "label": "frontend-dependencies",
            "type": "shell",
            "command": "cd ${workspaceFolder} && npm ci",
            "presentation": {
                "reveal": "silent",
                "revealProblems": "onProblem",
                "close": true
            }
        },
        {
            "label": "waiting-frontend-start",
            "type": "shell",
            "command": "while [[ $(ps -A | grep -c node) -lt 1 ]]; do echo 'Waiting for frontend to start...'; sleep 2; done",
            "presentation": {
                "reveal": "always",
                "panel": "new",
                "showReuseMessage": false,
                "close": true
            }
        }
    ]
}
```

> Note: This task will keep invoking installation method to **avoid missing dependencies** on start the application, which occur in development

When you are ready to create a _merge request_, run a typescript verification, to avoid errors types or unused calls

```bash
npm run verify
```

And create a version of your commits history changes, run
```bash
npm run version
```

[](#componentes)

<details>
<summary>Notification Componentes</summary>

> Note: All notifications componentes that need to use many times will be on notification context

### Loading

you'll use this component call when you want to force the user (client) to wait for something, like a request from the server (backend) or something like that

#### How to use Loading

First of all, you need to import the custom hook call named `useNotification`, to enable to call the loading methods

1. import the hook

```javascript
import { useNotification } from "@/contexts"
```

2. Added the hook call on component

```javascript
const { Loading } = useNotification()
```

Example:

```javascript
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Loading } = useNotification()

    /* Rest of component... */
}
```

3. Calling **Loading** actions on the component

```javascript
Loading.show("Loading description...")
Loading.hide()
```

> Note: By default, the loading description is **optional**, but you can override this passing a custom _simple text_ description or _ReactNode_ element

```javascript
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Loading } = useNotification()

    async function getUserData() {
        try {
            Loading.show("Getting user data...")
        } catch (error) {
            /* Handle error... */
        } finally {
            Loading.hide()
        }
    }
    /* Rest of component... */
}
```

### Toast

you'll use this component call when you want to show the user (client) what happens when the user did some actions, or the server(backend) responses, like a request from the server (backend), success on submit, error on submit and warnings

#### How to use Toast

First of all, you need to import the custom hook call named `useNotification`, to enable to call the loading methods

1. import the hook

```javascript
import { useNotification } from "@/contexts"
```

2. Added the hook call on component

```javascript
const { Toast } = useNotification()
```

Example:

```javascript
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Toast } = useNotification()

    /* Rest of component... */
}
```

3. Calling **Toast** actions on the component

```javascript
Toast.show("error", "Toast title", "Toast description...")
```

> Note: By default, Toast already has the automatic closing method called by delay

Example:

```javascript
import { ToastMessage } from "primereact/toast"
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Toast } = useNotification()

    async function submitUserData() {
        const toastTitle = "Submit user data"
        let toastType: ToastMessage["severity"] = "success"
        let toastDescription = "The user was successfully submitted"
        try {
            /* Handle submit... */
        } catch {
            toastType = "error"
            toastDescription = "An error occured, the user couldn't be submitted, try again later"
        } finally {
            Toast.show(toastType, toastTitle, toastDescription)
        }
    }
    /* Rest of component... */
}
```

</details>

[](#patterns)

<details>
<summary>Patterns</summary>

### Code auto format on save

For patterns code format in this project in Visual Studio Code you need to install this extension `esbenp.prettier-vscode` and include these `settings` to maintain the code format patterns automatically provided by the `prettier` extension, added in `.vscode/settings.json`

```json
{
    /**     Formatter    **/
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "prettier.configPath": ".prettierrc.json",
    "prettier.ignorePath": ".prettierignore",
    "editor.formatOnSave": true
}
```

> Note: It's extremely important to maintain the code format pattern to avoid unnecessary time adjusting manually

If you don't want to install the extension you can manually format the code running this command:

```bash
npm run format
```

### Commits

When committing your code you **MUST** add one of the following tags to the start of your commit:

-   **fix**: You fixed a bug;
-   **feature**: You added new functionality, module or changed how another feature works;
-   **refactor**: You reimplemented a functionality;
-   **docs**: You added documentation to a piece of code, this readme ou changed the changelog template;
-   **ci**: You modified in any way the file gitlab-ci;
-   **test**: You added new tests, changed existing ones or update test dependencies;
-   **security**: You added or fixed a security flaw;
-   **deprecated**: You set a feature as deprecated; or
-   **remove**: You removed a feature.

Structure to commit:
**"tag:" "#task id" "message"**

Example:

```
docs: #1234 my message
```

### Colors and styles

This project is based on bootstrap 5, react-boostrap and primereact, all styles are located in the _styles folder_, we use `scss` instead of `css`, it's simpler and more practical to use, if you need to use scss module for specific styles you can create the file directly on the folder of your component instead of styles folder.

All primereact components is changed to be similar of the custom bootstrap styles, if you see something different or wrong, check if the scss of primereact was overwritted.

This project uses bootstrap 5 class names instead of primeflex classes, so the pattern is based on bootstrap classes, so you can use bootstrap classes colors, texts, alignments, flex options, and others...

> Note: Primereact some components has `severity` propertie that was similar to `variant` propertie on react-bootstrap

### Component

When you create a component you must avoid this situations:

```javascript
export const myComponent = () => {
    function doSomething() {
        /* Your function*/
    }
    return (
        <>
            <button
                style={{ backgroundColor: "white", borderWidth: 1 }}
                onClick={() => {
                    console.log("clicked")
                    doSomething()
                }}
            >
                Action
            </button>
        </>
    )
}
```

The problems here are:

1. The component name must be in PascalCase, when trying to use `<myComponent />` it will not work
2. myComponent.style has an object which means react on new rendering will see the object in the style and consider the previous versions to be the same as the current rendering (myComponent.style object is the same as the previous version) and then return false because it is comparing object to object, use className instead of manually styling
3. myComponent.onClick has an anonymous function, it will be recreated on every render, in cases when you use `.map` like this example, will get a worse performance, so use a named function instead.

correct example:

```javascript
export const MyComponent = () => {
    function doSomething() {
        /* Your function*/
    }
    return (
        <button className="btn-style" onClick={doSomething}>
            Action
        </button>
    )
}
```

#### DataTable
When create a DataTable `columns`, you must need to create a file named `ColumnsConfig`, to easy modified the column of datatable

### Structures organization

For better organization and useful coding, you'll should keep these organization for easier access, adjust, add and remove features

#### Variables, functions, classes, interfaces, types, files and folders

1. Variables and functions:
   Must be on **camelCase**

example:

```javascript
function myFunction() {
    const myFirstVariable = 123
    let mySecondVariable = "abc"
}
```

2. Classes, interfaces, types, files and folders
   All Classes, interfaces, types, files (component JSX) and Folder (will export Component) must be on **PascalCase**, except Helpers

example:

```typescript
class MyClass() {}

interface IMyInterface {}

type TMyType = {}

/*
MyFirstComponent.tsx          <--- The exported component name must be the name of the file
MySecondComponent/index.tsx   <--- The exported component name must be the name of the folder
*/
```

Remember that some complex components need to be reparted into small files in folders(if the single component part has too much logic that need to reparted again, like a page that has a DataTable and a lot of options on the DataTable) to avoid large codes that sometimes need to be rewritten.
All Components must be started with **PascalCase**, except when the file name is _index_, if this occured the component name must be the **folder name**.

```
src
 | /@types       <---- The types of packages that need to be declared for TypeScript can be understood, these types of files end with `.d.ts`
 | /assets       <---- Used to store images and icons
 | /components   <---- All JSX components that are used a lot of times to show something, don't put helpers on this folder, helpers will be placed on `utils` folder
 | /configs      <---- Configuration of certain components like Auth, Websocket that uses environments
 | /constants    <---- Constants that can't be changed
 | /contexts     <---- All contexts declarations
 | /dev          <---- All development configurations that will be **deleted on build**
 | /interfaces   <---- All repetitive interfaces that can be used in other components a lot of times, if you create an interface that will only used on the same folder, you don't need to put on interfaces folder
 | /pages        <---- All views
 | /routes       <---- All routes
 | /styles       <---- All scss styles
 | /utils        <---- All helpers like formats, custom adjusts and others...
```

##### Organize the files into folder

```
src
 | /components
 |  | /Button.tsx       <---- Simple component that doens't require small files
    | /Modal            <---- Complex component that need to be reparted with small files
    |   | Header.tsx
    |   | Body.tsx
    |   | ModalFooter.tsx
    |   | Base.tsx      <---- Base of modal (optional to use overwritted with Object.assign to keep call by the folder name like <Modal> and not <Modal.Modal>)
    |   | index.ts      <---- Group of exports for "/components/Modal/*" for easier import
    | /Card             <---- Multiples similar files of Card type that can be used by unique call
    |   | Details.tsx
    |   | Table.tsx
    |   | index.ts      <---- Group of exports for "/components/Card/*" for easier import
```

Example of `index.ts` for `/components/Modal/index.ts`

```javascript
import { Header } from "./Header"
import { Body } from "./Body"
import { ModalFooter } from "./ModalFooter"
import { Base } from "./Base"

// Optional, if you want to use <Modal.Base> you don't need to do that, just use `export * as on /components`
export const Modal = Object.assign(Base, {
    Header,
    Body,
    ModalFooter,
})
```

Example of `index.ts` for `/components/Card/index.ts`

```
export { Details } from "./Details"
export { Table } from "./Table"
```

Example of `index.ts` for `/components/index.ts`

```javascript
export { Button } from "./Button"
export * from "./Modal"
export * as Card from "./Card"
```

Organizing like this you can easily import your own components/JSX files, doing this

```javascript
//example of import on /pages calling a multiples components
import { Button, Modal, Card } from "@/components"

//example of using
export const MyComponent = () => {
    return (
        <>
            <Card.Details>
                {/* Rest of component... */}
                <Button>My Button</Button>
            </Card.Details>
            <Card.Table />
            <Modal>
                <Modal.Header>Title of Modal</Modal.Header>
                <Modal.Body>Body of Modal</Modal.Body>
                <Modal.ModalFooter>
                    <Button>My cancel action</Button>
                    <Button>My confirm action</Button>
                </Modal.ModalFooter>
            </Modal>
        </>
    )
}
```

If you don't do that, the import calls will be like this:

```javascript
//example of import on /pages calling a multiples components
import { Button } from "@/components/Button"
import { Base } from "@/components/Modal/Base"
import { Header } from "@/components/Modal/Header"
import { Body } from "@/components/Modal/Body"
import { ModalFooter } from "@/components/Modal/ModalFooter"
import { Details } from "@/components/Card/Details"
import { Table } from "@/components/Card/Table"

//example of using
export const MyComponent = () => {
    return (
        <>
            <Details>
                {/* Rest of component... */}
                <Button>My Button</Button>
            </Details>
            <Table />
            <Base>
                <Header>Title of Modal</Header>
                <Body>Body of Modal</Body>
                <ModalFooter>
                    <Button>My cancel action</Button>
                    <Button>My confirm action</Button>
                </ModalFooter>
            </Base>
        </>
    )
}
```

#### Routes

All pages must be imported by lazy loading on routes to avoid unnecessary imports of all pages when the front end starts.
The pages has a lot of complexity components, params, logic and handles, to avoid performance issues, the imports of pages should called by lazy imports, some complex components too
Example of import default:

```javascript
const Version = lazy(() => import("@/pages/Version"))
```

##### Navigation

All navigation methods must be used Link components that implements react-router-dom navigation, to avoid refreshing the html document on navigate to another route, avoid use

```javascript
<a href="/my_route">My route</a>
```

Correct navigation

```javascript
<Link to={route}>My route</Link>
```

</details>

### Observation

### Constants routes
When create a new route you must specify on enum of `RouteMapKeys` , if the route is nested, you need to specify the current path with `.`, use the same prefix name to simplify route name.

To get the complete route path to avoid concat every single path, use the `getCompleteRouteMap`, you need to specify the route (`RouteMapKeys`). by default the DataTable custom component has the `exportFilenameRoute`, you need to add the `RouteMapKeys`, to apply the current concact title of routes.

###` Datatable
When use Datatable, if can export file, add the `exportFilenameRoute` to specify the current datatable route that will consider to export with the complete route name, to avoid generic name
# frontend-copa

## Getting started

On this project you need to have already installed **Node.js** to start the project, if you don't have it installed, keep following the instructions

### Installing Node.js and NVM (Node Version Manager)

```bash
# installs nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash

# download and install Node.js (you may need to restart the terminal)
nvm install 22

# verifies the right Node.js version is in the environment
node -v
# should print `v22.11.0`

# verifies the right npm version is in the environment
npm -v
# should print `10.9.0`
```

Then install on the project folder all dependencies:

```bash
npm ci && npm start
```

And lastly change the default behavior of husky so that you can actually make a commit:

```bash
echo "npx commitlint --version" > .husky/pre-commit
```

**Everything should be good to go**, but, for future reference, you can configure your environment with the following commands:

```bash
npm ci
npx husky init
echo "npx commitlint --version" > .husky/pre-commit
echo "npx --no -- commitlint --verbose --config commitlint.config.js --edit \$1" > .husky/commit-msg
echo "export HUSKY=0
npm run changelog
export HUSKY=1" > .husky/pre-push
```

## Start Front-end React

First of all create a `vite.config.ts` on the root folder like this:
```javascript
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tsconfigPaths from "vite-tsconfig-paths"
import { fileURLToPath } from "node:url"

function devFilesPathToExclude() {
    const filesPath = ["src/dev/*"]
    return filesPath.map((src) => {
        return fileURLToPath(new URL(src, import.meta.url))
    })
}

// https://vite.dev/config/
export default defineConfig({
    define: {
        "process.env": process.env,
    },
    plugins: [react(), tsconfigPaths()],
    envPrefix: "COPA_",
    build: {
        outDir: "dist",
        chunkSizeWarningLimit: 400,
        sourcemap: false,
        rollupOptions: {
            external: [...devFilesPathToExclude()],
            output: {
                manualChunks(id) {
                    if (id.includes("/src/pages/")) {
                        const route = id.match(/\/src\/pages\/(\w+)/)
                        if (route && route[1]) {
                            return `page-${route[1]}`
                        }
                    }

                    if (id.includes("bootstrap")) {
                        return "bootstrap"
                    }
                },
            },
        },
    },
})

```

Make a copy of the `.env.example` file and rename it to `.env`
```bash
cp .env.example .env
```
Lastly, create a new file called `version.json` in your root folder with this content:
```json
{"version": "v1.0.0", "date": "2025-01-01"}
```
To run this project, manually just open a terminal and run:

```bash
npm ci && npm start
```

> Note: By default the front-end port will be `5173`

For Visual Studio Code, you can set up a launch to start and debug the application using these launchs on `.vscode/launch.json`

```json
{
    "configurations": [
        {
            "name": "Start Front-end",
            "type": "node",
            "request": "launch",
            "cwd": "${workspaceFolder}",
            "runtimeExecutable": "npm",
            "runtimeArgs": ["start"],
            "console": "internalConsole",
            "preLaunchTask": "frontend-dependencies"
        },
        {
            "name": "Debug Front-end",
            "type": "chrome",
            "request": "launch",
            "url": "http://localhost:5173",
            "webRoot": "${workspaceFolder}",
            "preLaunchTask": "waiting-frontend-start"
        }
    ],
    "compounds": [
        {
            "name": "Start and Debug Front-end",
            "configurations": ["Start Front-end", "Debug Front-end"],
            "stopAll": true
        }
    ]
}
```

> Note: With **compounds** you can start both launchs (_Start Front-end + Debug Front-end_) on the same time

You need to add also `preLaunchTask` named `frontend-dependencies` and `waiting-frontend-start` on `.vscode/tasks.json`

```json
{
    "tasks": [
        {
            "label": "frontend-dependencies",
            "type": "shell",
            "command": "cd ${workspaceFolder} && npm ci",
            "presentation": {
                "reveal": "silent",
                "revealProblems": "onProblem",
                "close": true
            }
        },
        {
            "label": "waiting-frontend-start",
            "type": "shell",
            "command": "while [[ $(ps -A | grep -c node) -lt 1 ]]; do echo 'Waiting for frontend to start...'; sleep 2; done",
            "presentation": {
                "reveal": "always",
                "panel": "new",
                "showReuseMessage": false,
                "close": true
            }
        }
    ]
}
```

> Note: This task will keep invoking installation method to **avoid missing dependencies** on start the application, which occur in development

When you are ready to create a _merge request_, run a typescript verification, to avoid errors types or unused calls

```bash
npm run verify
```

And create a version of your commits history changes, run
```bash
npm run version
```

[](#componentes)

<details>
<summary>Notification Componentes</summary>

> Note: All notifications componentes that need to use many times will be on notification context

### Loading

you'll use this component call when you want to force the user (client) to wait for something, like a request from the server (backend) or something like that

#### How to use Loading

First of all, you need to import the custom hook call named `useNotification`, to enable to call the loading methods

1. import the hook

```javascript
import { useNotification } from "@/contexts"
```

2. Added the hook call on component

```javascript
const { Loading } = useNotification()
```

Example:

```javascript
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Loading } = useNotification()

    /* Rest of component... */
}
```

3. Calling **Loading** actions on the component

```javascript
Loading.show("Loading description...")
Loading.hide()
```

> Note: By default, the loading description is **optional**, but you can override this passing a custom _simple text_ description or _ReactNode_ element

```javascript
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Loading } = useNotification()

    async function getUserData() {
        try {
            Loading.show("Getting user data...")
        } catch (error) {
            /* Handle error... */
        } finally {
            Loading.hide()
        }
    }
    /* Rest of component... */
}
```

### Toast

you'll use this component call when you want to show the user (client) what happens when the user did some actions, or the server(backend) responses, like a request from the server (backend), success on submit, error on submit and warnings

#### How to use Toast

First of all, you need to import the custom hook call named `useNotification`, to enable to call the loading methods

1. import the hook

```javascript
import { useNotification } from "@/contexts"
```

2. Added the hook call on component

```javascript
const { Toast } = useNotification()
```

Example:

```javascript
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Toast } = useNotification()

    /* Rest of component... */
}
```

3. Calling **Toast** actions on the component

```javascript
Toast.show("error", "Toast title", "Toast description...")
```

> Note: By default, Toast already has the automatic closing method called by delay

Example:

```javascript
import { ToastMessage } from "primereact/toast"
import { useNotification } from "@/contexts"

export const MyComponent = () => {
    const { Toast } = useNotification()

    async function submitUserData() {
        const toastTitle = "Submit user data"
        let toastType: ToastMessage["severity"] = "success"
        let toastDescription = "The user was successfully submitted"
        try {
            /* Handle submit... */
        } catch {
            toastType = "error"
            toastDescription = "An error occured, the user couldn't be submitted, try again later"
        } finally {
            Toast.show(toastType, toastTitle, toastDescription)
        }
    }
    /* Rest of component... */
}
```

</details>

[](#patterns)

<details>
<summary>Patterns</summary>

### Code auto format on save

For patterns code format in this project in Visual Studio Code you need to install this extension `esbenp.prettier-vscode` and include these `settings` to maintain the code format patterns automatically provided by the `prettier` extension, added in `.vscode/settings.json`

```json
{
    /**     Formatter    **/
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "prettier.configPath": ".prettierrc.json",
    "prettier.ignorePath": ".prettierignore",
    "editor.formatOnSave": true
}
```

> Note: It's extremely important to maintain the code format pattern to avoid unnecessary time adjusting manually

If you don't want to install the extension you can manually format the code running this command:

```bash
npm run format
```

### Commits

When committing your code you **MUST** add one of the following tags to the start of your commit:

-   **fix**: You fixed a bug;
-   **feature**: You added new functionality, module or changed how another feature works;
-   **refactor**: You reimplemented a functionality;
-   **docs**: You added documentation to a piece of code, this readme ou changed the changelog template;
-   **ci**: You modified in any way the file gitlab-ci;
-   **test**: You added new tests, changed existing ones or update test dependencies;
-   **security**: You added or fixed a security flaw;
-   **deprecated**: You set a feature as deprecated; or
-   **remove**: You removed a feature.

Structure to commit:
**"tag:" "#task id" "message"**

Example:

```
docs: #1234 my message
```

### Colors and styles

This project is based on bootstrap 5, react-boostrap and primereact, all styles are located in the _styles folder_, we use `scss` instead of `css`, it's simpler and more practical to use, if you need to use scss module for specific styles you can create the file directly on the folder of your component instead of styles folder.

All primereact components is changed to be similar of the custom bootstrap styles, if you see something different or wrong, check if the scss of primereact was overwritted.

This project uses bootstrap 5 class names instead of primeflex classes, so the pattern is based on bootstrap classes, so you can use bootstrap classes colors, texts, alignments, flex options, and others...

> Note: Primereact some components has `severity` propertie that was similar to `variant` propertie on react-bootstrap

### Component

When you create a component you must avoid this situations:

```javascript
export const myComponent = () => {
    function doSomething() {
        /* Your function*/
    }
    return (
        <>
            <button
                style={{ backgroundColor: "white", borderWidth: 1 }}
                onClick={() => {
                    console.log("clicked")
                    doSomething()
                }}
            >
                Action
            </button>
        </>
    )
}
```

The problems here are:

1. The component name must be in PascalCase, when trying to use `<myComponent />` it will not work
2. myComponent.style has an object which means react on new rendering will see the object in the style and consider the previous versions to be the same as the current rendering (myComponent.style object is the same as the previous version) and then return false because it is comparing object to object, use className instead of manually styling
3. myComponent.onClick has an anonymous function, it will be recreated on every render, in cases when you use `.map` like this example, will get a worse performance, so use a named function instead.

correct example:

```javascript
export const MyComponent = () => {
    function doSomething() {
        /* Your function*/
    }
    return (
        <button className="btn-style" onClick={doSomething}>
            Action
        </button>
    )
}
```

#### DataTable
When create a DataTable `columns`, you must need to create a file named `ColumnsConfig`, to easy modified the column of datatable

### Structures organization

For better organization and useful coding, you'll should keep these organization for easier access, adjust, add and remove features

#### Variables, functions, classes, interfaces, types, files and folders

1. Variables and functions:
   Must be on **camelCase**

example:

```javascript
function myFunction() {
    const myFirstVariable = 123
    let mySecondVariable = "abc"
}
```

2. Classes, interfaces, types, files and folders
   All Classes, interfaces, types, files (component JSX) and Folder (will export Component) must be on **PascalCase**, except Helpers

example:

```typescript
class MyClass() {}

interface IMyInterface {}

type TMyType = {}

/*
MyFirstComponent.tsx          <--- The exported component name must be the name of the file
MySecondComponent/index.tsx   <--- The exported component name must be the name of the folder
*/
```

Remember that some complex components need to be reparted into small files in folders(if the single component part has too much logic that need to reparted again, like a page that has a DataTable and a lot of options on the DataTable) to avoid large codes that sometimes need to be rewritten.
All Components must be started with **PascalCase**, except when the file name is _index_, if this occured the component name must be the **folder name**.

```
src
 | /@types       <---- The types of packages that need to be declared for TypeScript can be understood, these types of files end with `.d.ts`
 | /assets       <---- Used to store images and icons
 | /components   <---- All JSX components that are used a lot of times to show something, don't put helpers on this folder, helpers will be placed on `utils` folder
 | /configs      <---- Configuration of certain components like Auth, Websocket that uses environments
 | /constants    <---- Constants that can't be changed
 | /contexts     <---- All contexts declarations
 | /dev          <---- All development configurations that will be **deleted on build**
 | /interfaces   <---- All repetitive interfaces that can be used in other components a lot of times, if you create an interface that will only used on the same folder, you don't need to put on interfaces folder
 | /pages        <---- All views
 | /routes       <---- All routes
 | /styles       <---- All scss styles
 | /utils        <---- All helpers like formats, custom adjusts and others...
```

##### Organize the files into folder

```
src
 | /components
 |  | /Button.tsx       <---- Simple component that doens't require small files
    | /Modal            <---- Complex component that need to be reparted with small files
    |   | Header.tsx
    |   | Body.tsx
    |   | ModalFooter.tsx
    |   | Base.tsx      <---- Base of modal (optional to use overwritted with Object.assign to keep call by the folder name like <Modal> and not <Modal.Modal>)
    |   | index.ts      <---- Group of exports for "/components/Modal/*" for easier import
    | /Card             <---- Multiples similar files of Card type that can be used by unique call
    |   | Details.tsx
    |   | Table.tsx
    |   | index.ts      <---- Group of exports for "/components/Card/*" for easier import
```

Example of `index.ts` for `/components/Modal/index.ts`

```javascript
import { Header } from "./Header"
import { Body } from "./Body"
import { ModalFooter } from "./ModalFooter"
import { Base } from "./Base"

// Optional, if you want to use <Modal.Base> you don't need to do that, just use `export * as on /components`
export const Modal = Object.assign(Base, {
    Header,
    Body,
    ModalFooter,
})
```

Example of `index.ts` for `/components/Card/index.ts`

```
export { Details } from "./Details"
export { Table } from "./Table"
```

Example of `index.ts` for `/components/index.ts`

```javascript
export { Button } from "./Button"
export * from "./Modal"
export * as Card from "./Card"
```

Organizing like this you can easily import your own components/JSX files, doing this

```javascript
//example of import on /pages calling a multiples components
import { Button, Modal, Card } from "@/components"

//example of using
export const MyComponent = () => {
    return (
        <>
            <Card.Details>
                {/* Rest of component... */}
                <Button>My Button</Button>
            </Card.Details>
            <Card.Table />
            <Modal>
                <Modal.Header>Title of Modal</Modal.Header>
                <Modal.Body>Body of Modal</Modal.Body>
                <Modal.ModalFooter>
                    <Button>My cancel action</Button>
                    <Button>My confirm action</Button>
                </Modal.ModalFooter>
            </Modal>
        </>
    )
}
```

If you don't do that, the import calls will be like this:

```javascript
//example of import on /pages calling a multiples components
import { Button } from "@/components/Button"
import { Base } from "@/components/Modal/Base"
import { Header } from "@/components/Modal/Header"
import { Body } from "@/components/Modal/Body"
import { ModalFooter } from "@/components/Modal/ModalFooter"
import { Details } from "@/components/Card/Details"
import { Table } from "@/components/Card/Table"

//example of using
export const MyComponent = () => {
    return (
        <>
            <Details>
                {/* Rest of component... */}
                <Button>My Button</Button>
            </Details>
            <Table />
            <Base>
                <Header>Title of Modal</Header>
                <Body>Body of Modal</Body>
                <ModalFooter>
                    <Button>My cancel action</Button>
                    <Button>My confirm action</Button>
                </ModalFooter>
            </Base>
        </>
    )
}
```

#### Routes

All pages must be imported by lazy loading on routes to avoid unnecessary imports of all pages when the front end starts.
The pages has a lot of complexity components, params, logic and handles, to avoid performance issues, the imports of pages should called by lazy imports, some complex components too
Example of import default:

```javascript
const Version = lazy(() => import("@/pages/Version"))
```

##### Navigation

All navigation methods must be used Link components that implements react-router-dom navigation, to avoid refreshing the html document on navigate to another route, avoid use

```javascript
<a href="/my_route">My route</a>
```

Correct navigation

```javascript
<Link to={route}>My route</Link>
```

</details>

### Observation

### Constants routes
When create a new route you must specify on enum of `RouteMapKeys` , if the route is nested, you need to specify the current path with `.`, use the same prefix name to simplify route name.

To get the complete route path to avoid concat every single path, use the `getCompleteRouteMap`, you need to specify the route (`RouteMapKeys`). by default the DataTable custom component has the `exportFilenameRoute`, you need to add the `RouteMapKeys`, to apply the current concact title of routes.

###` Datatable
When use Datatable, if can export file, add the `exportFilenameRoute` to specify the current datatable route that will consider to export with the complete route name, to avoid generic name
