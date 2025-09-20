import { user } from "@web/core/user";
import {SearchModel}  from "@web/search/search_model"
import { patch } from "@web/core/utils/patch";
import {
    constructDateDomain,
    DEFAULT_INTERVAL,
    getComparisonOptions,
    getIntervalOptions,
    getPeriodOptions,
    rankInterval,
    yearSelected,
} from "@web/search/utils/dates";
const { DateTime } = luxon;
patch(SearchModel.prototype, {
  _getDateFilterDomain(dateFilter, generatorIds, key = "domain") {
    const { fieldName, fieldType } = dateFilter;
    let dateFilterRange;
    if ("jalali" == "jalali") {
      dateFilterRange = jConstructDateDomain(
        this.referenceMoment,
        dateFilter,
        generatorIds,
      );
    } else {
      dateFilterRange = constructDateDomain(
        this.referenceMoment,
        dateFilter,
        generatorIds,
      );
    }
    return dateFilterRange[key];
  },
  getFullComparison() {
    let searchItem = null;
    for (const queryElem of this.query.slice().reverse()) {
      const item = this.searchItems[queryElem.searchItemId];
      if (item.type === "comparison") {
        searchItem = item;
        break;
      } else if (item.type === "favorite" && item.comparison) {
        searchItem = item;
        break;
      }
    }
    if (!searchItem) {
      return null;
    } else if (searchItem.type === "favorite") {
      return searchItem.comparison;
    }
    const { dateFilterId, comparisonOptionId } = searchItem;
    const dateFilter = this.searchItems[dateFilterId];
    const { fieldName, description: dateFilterDescription } = dateFilter;
    const selectedGeneratorIds = this._getSelectedGeneratorIds(dateFilterId);
    let range, rangeDescription, comparisonRange, comparisonRangeDescription;
    if (session.user_context.calendar == "jalali") {
      ({ domain: range, description: rangeDescription } =
        jalaliConstructDateDomain(
          this.referenceMoment,
          dateFilter,
          selectedGeneratorIds,
        ));
      ({ domain: comparisonRange, description: comparisonRangeDescription } =
        jalaliConstructDateDomain(
          this.referenceMoment,
          dateFilter,
          selectedGeneratorIds,
          comparisonOptionId,
        ));
    } else {
      ({ domain: range, description: rangeDescription } = constructDateDomain(
        this.referenceMoment,
        dateFilter,
        selectedGeneratorIds,
      ));
      ({ domain: comparisonRange, description: comparisonRangeDescription } =
        constructDateDomain(
          this.referenceMoment,
          dateFilter,
          selectedGeneratorIds,
          comparisonOptionId,
        ));
    }
    return {
      comparisonId: comparisonOptionId,
      fieldName,
      fieldDescription: dateFilterDescription,
      range: range.toList(),
      rangeDescription,
      comparisonRange: comparisonRange.toList(),
      comparisonRangeDescription,
    };
  },
  _enrichItem(searchItem) {
    if (searchItem.type === "field" && searchItem.fieldType === "properties") {
      return {
        ...searchItem,
      };
    }
    const queryElements = this.query.filter(
      (queryElem) => queryElem.searchItemId === searchItem.id,
    );
    const isActive = Boolean(queryElements.length);
    const enrichSearchItem = Object.assign(
      {
        isActive,
      },
      searchItem,
    );
    function _enrichOptions(options, selectedIds) {
      return options.map((o) => {
        const { description, id, groupNumber } = o;
        const isActive = selectedIds.some((optionId) => optionId === id);
        return {
          description,
          id,
          groupNumber,
          isActive,
        };
      });
    }
    switch (searchItem.type) {
      case "comparison": {
        const { dateFilterId } = searchItem;
        const dateFilterIsActive = this.query.some(
          (queryElem) =>
            queryElem.searchItemId === dateFilterId &&
            !queryElem.generatorId.startsWith("custom"),
        );
        if (!dateFilterIsActive) {
          return null;
        }
        break;
      }
      case "dateFilter":
        if (user.context.calendar === "jalali") {
          const data = getPeriodOptions(
            this.referenceMoment,
            searchItem.optionsParams,
          );
          enrichSearchItem.options = _enrichOptions(
            jalaliGetPeriodOptions(this.referenceMoment, data),
            queryElements.map((queryElem) => queryElem.generatorId),
          );
        } else {
          enrichSearchItem.options = _enrichOptions(
            getPeriodOptions(this.referenceMoment, searchItem.optionsParams),
            queryElements.map((queryElem) => queryElem.generatorId),
          );
        }
        break;
      case "dateGroupBy":
        enrichSearchItem.options = _enrichOptions(
          this.intervalOptions,
          queryElements.map((queryElem) => queryElem.intervalId),
        );
        break;
      case "field":
      case "field_property":
        enrichSearchItem.autocompleteValues = queryElements.map(
          (queryElem) => queryElem.autocompleteValue,
        );
        break;
    }
    return enrichSearchItem;
  },
});
