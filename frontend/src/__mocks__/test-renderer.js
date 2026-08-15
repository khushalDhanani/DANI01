const ReactTestRenderer = require("react-test-renderer");

module.exports = {
  ...ReactTestRenderer,
  createRoot: (options) => {
    let instance = null;
    return {
      render: (element) => {
        if (!instance) {
          instance = ReactTestRenderer.create(element, options);
        } else {
          instance.update(element);
        }
      },
      unmount: () => {
        if (instance) instance.unmount();
      },
      get container() {
        if (!instance) return null;
        const root = instance.root;
        if (root) {
          const proto = Object.getPrototypeOf(root);
          if (proto && !proto.queryAll) {
            proto.queryAll = function (predicate) {
              try {
                return this.findAll(predicate);
              } catch {
                return [];
              }
            };
          }
          if (proto && !proto.toJSON) {
            proto.toJSON = function () {
              return instance ? instance.toJSON() : null;
            };
          }
          root.toJSON = () => (instance ? instance.toJSON() : null);
        }
        return root;
      },
      get root() {
        return instance ? instance.root : null;
      },
      toJSON: () => (instance ? instance.toJSON() : null),
    };
  },
};
