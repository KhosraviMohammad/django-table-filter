class DropdownFilter {

    #defaultInputValue = {}

    constructor(element, onOpen, onClose, onEraser, onBackValue, onFilter) {
        this.element = $(element);
        this.onOpen = onOpen;
        this.onClose = onClose;
        this.onEraser = onEraser;
        this.onBackValue = onBackValue;
        this.onFilter = onFilter;
        this.findSpecificElements($(element));
        this.activateClick();
        this.activateDocument();
        this.activateEraser();

    }

    findSpecificElements(element) {
        this.openFilterBox = element.find('.open-filter-box');
        this.filterBox = element.find('.filter-box');
        this.eraserButton = element.find('.eraser-button');
        this.filterButton = element.find('.filter-button');
    }

    activateClick() {
        let dropDownFilterBox = this.element;
        let openFilterBox = this.openFilterBox;
        let filterBox = this.filterBox;
        let thisObject = this;
        $(openFilterBox).click(function (e) {
            if (filterBox.is(":visible")) {
                thisObject.onBackValue(e, dropDownFilterBox, filterBox, openFilterBox);
                thisObject.onClose(e, dropDownFilterBox, filterBox, openFilterBox);
            } else {
                thisObject.onOpen(e, dropDownFilterBox, filterBox, openFilterBox);
            }
        })
    }

    activateEraser() {
        let dropDownFilterBox = this.element;
        let openFilterBox = this.openFilterBox;
        let filterBox = this.filterBox;
        let eraserButton = this.eraserButton;
        let thisObject = this;
        $(eraserButton).click(function (e) {
            thisObject.onEraser(e, dropDownFilterBox, filterBox, openFilterBox);
        })
    }

    activateFilter() {
        let dropDownFilterBox = this.element;
        let openFilterBox = this.openFilterBox;
        let filterBox = this.filterBox;
        let filterButton = this.filterButton;
        let thisObject = this;
        $(filterButton).click(function (e) {
            thisObject.onFilter(e, dropDownFilterBox, filterBox, openFilterBox);
        })
    }

    activateDocument() {
        let dropDownFilterBox = this.element;
        let openFilterBox = this.openFilterBox;
        let filterBox = this.filterBox;
        let thisObject = this;
        $(document).click(function (e) {
            let targetElement = $(e.target)
            if (dropDownFilterBox !== targetElement && !dropDownFilterBox.has(targetElement).length && filterBox.is(":visible")) {
                thisObject.onBackValue(e, dropDownFilterBox, filterBox, openFilterBox);
                thisObject.onClose(e, dropDownFilterBox, filterBox, openFilterBox);

            }
        })
    }

    set defaultInputValue(NameValueObject) {
        this.#defaultInputValue[NameValueObject['name']] = NameValueObject['value'];
    }

    get defaultInputValue() {
        return this.#defaultInputValue
    }

}

jQuery.fn.extend({
    DropdownFilter: function (options = {}) {
        let onOpen = options.onOpen;
        let onClose = options.onClose;
        let onEraser = options.onEraser;
        let onBackValue = options.onBackValue;
        let onFilter = options.onFilter;
        if (typeof onOpen === 'undefined') {
            onOpen = function () {
            };
        }
        if (typeof onClose === 'undefined') {
            onClose = function () {
            };
        }
        if (typeof onEraser === 'undefined') {
            onEraser = function () {
            };
        }
        if (typeof onBackValue === 'undefined') {
            onBackValue = function () {
            };
        }
        if (typeof onFilter === 'undefined') {
            onFilter = function () {
            };
        }

        this.each(function () {
            this.dropDownFilter = new DropdownFilter(this, onOpen, onClose, onEraser, onBackValue, onFilter);
        });
    }
});

