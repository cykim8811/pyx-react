
# <img src="https://raw.githubusercontent.com/cykim8811/pyx-react/main/assets/pyx.svg" width="30" height="30"> PyX Framework


## Introduction
PyX Framework is a framework that enables Python objects to be easily rendered on a web server. This allows Python developers to integrate their backend logic with web interfaces seamlessly.

## Features
- **Automatic Rendering**: Implement `__render__(self, user)` in Python objects to display them as web components.
- **Event Handling**: Easily handle user interactions with Python methods.
- **Dynamic Updates**: Changes in Python object states are automatically reflected in the web interface.

## Installation
To install PyX Framework, use pip:

```bash
pip install pyx-react
```

or clone this repository:

```bash
git clone https://github.com/cykim8811/pyx-react.git
cd pyx-react
python setup.py install
```

To install vscode extension, search for `pyx-react` in vscode extension marketplace.

## Usage
Here's a simple example of how to use PyX Framework:

```python

from pyx import createElement, App

class Counter:
    def __init__(self):
        self.count = 8

    def increment(self, e):
        if e.button == 0:
            self.count += 1

    def __render__(self, user):
        return createElement('div', None,
            createElement('div', None, f'count: {self.count}'),
            createElement('button', {'onClick': self.increment}, 'Increment')
        )

#    JSX-like syntax (Not supported yet)
#    def __render__(self, user):
#        return (
#            <div>
#                <div>count: {self.count}</div>
#                <button onClick={self.increment}>Increment</button>
#            </div>
#        )


app = App(Counter())
app.run(host='0.0.0.0', port=8080)


```
### Result
![result](https://raw.githubusercontent.com/cykim8811/pyx-react/main/assets/screenshot_1.gif)

## Documentation
No documentation is available at the moment. Please refer to the examples for more information.

## Contributing
Contributions to PyX Framework are welcome!

## License
PyX Framework is licensed under MIT License.

## Contact
cykim8811@snu.ac.kr
