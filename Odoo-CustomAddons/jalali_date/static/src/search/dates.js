import { Domain } from "@web/core/domain";
import { serializeDate, serializeDateTime } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
import { user } from "@web/core/user";
import { _t } from "@web/core/l10n/translation";
import * as DatesUtils  from "@web/search/utils/dates"
import { JalaliStartOf,JalaliEndOf, jDate } from "../jutils";
const {DateTime} = luxon;
export const QUARTERS = {
    1: { description: _t("Q1"), coveredMonths: [1, 2, 3] },
    2: { description: _t("Q2"), coveredMonths: [4, 5, 6] },
    3: { description: _t("Q3"), coveredMonths: [7, 8, 9] },
    4: { description: _t("Q4"), coveredMonths: [10, 11, 12] },
};

export const QUARTER_OPTIONS = {
    fourth_quarter: {
        id: "fourth_quarter",
        groupNumber: 1,
        description: QUARTERS[4].description,
        setParam: { quarter: 4 },
        granularity: "quarter",
    },
    third_quarter: {
        id: "third_quarter",
        groupNumber: 1,
        description: QUARTERS[3].description,
        setParam: { quarter: 3 },
        granularity: "quarter",
    },
    second_quarter: {
        id: "second_quarter",
        groupNumber: 1,
        description: QUARTERS[2].description,
        setParam: { quarter: 2 },
        granularity: "quarter",
    },
    first_quarter: {
        id: "first_quarter",
        groupNumber: 1,
        description: QUARTERS[1].description,
        setParam: { quarter: 1 },
        granularity: "quarter",
    },
};

const JALALI_MONTH_TO_RANGE  = {
    1: 1,
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 3,
    8: 3,
    9: 3,
    10: 4,
    11: 4,
    12: 4,
};

// function jalaliGetPeriodOptions(referenceMoment, date_make) {
//     const options = [];
//     const periodOptionsResult = [];
//     const currentGregorianYear = referenceMoment.year;
//     const originalOptions = date_make;
//     for (const option of originalOptions) {
//         if (!option || !option.id) {
//             console.warn("Skipping invalid option:", option);
//             continue;
//         }
//         const {id, groupNumber} = option;
//         let description = option.description;
//         let dateForDesc = referenceMoment;
//         if (description && typeof description === "object" && description.toString && description.constructor.name === "LazyTranslatedString") {
//             description = description.toString();
//         }
//         if ((option.granularity === "year" || id.startsWith("year")) && description && /^\d{4}$/.test(String(description))) {
//             const gregorianYearStr = String(description);
//             try {
//                 if (!toJalaali)
//                     throw new Error("toJalaali function is not available!");
//                 let dateForConversion;
//                 if (option.plusParam?.years !== undefined) {
//                     dateForConversion = referenceMoment.plus(option.plusParam);
//                 } else {
//                     dateForConversion = DateTime.fromObject({
//                         year: parseInt(gregorianYearStr, 10),
//                     });
//                 }
//                 const jalaliResult = toJalaali(dateForConversion.year, dateForConversion.month, dateForConversion.day);
//                 if (jalaliResult && typeof jalaliResult.jy !== "undefined") {
//                     description = jalaliResult.jy.toString();
//                 } else {
//                     console.warn("Jalali conversion did not return 'jy'. Using original:", gregorianYearStr);
//                     description = gregorianYearStr;
//                 }
//             } catch (e) {
//                 console.error("Error during Jalali conversion:", e);
//                 description = gregorianYearStr;
//             }
//         } else if (option.granularity === "quarter" && option.setParam?.quarter) {
//             const quarterNum = option.setParam.quarter;
//             switch (quarterNum) {
//             case 1:
//                 description = _t("Winter");
//                 break;
//             case 2:
//                 description = _t("Spring");
//                 break;
//             case 3:
//                 description = _t("Summer");
//                 break;
//             case 4:
//                 description = _t("Autumn");
//                 break;
//             default:
//                 description = option.description?.toString() || id;
//                 break;
//             }
//         }
//         periodOptionsResult.push({
//             id: id,
//             groupNumber: groupNumber,
//             description: description,
//             defaultYearId: option.defaultYearId || "year",
//         });
//     }
//     return periodOptionsResult;
// }
    
// function jalaliConstructDateDomain(referenceMoment, dateFilter, selectedOptionIds, comparisonOptionId=null) {
//     const {fieldName, fieldType} = dateFilter;
//     if (!fieldName || !fieldType) {
//         console.error("Could not extract fieldName or fieldType from dateFilter:", dateFilter);
//         return {
//             domain: dateFilter.domain || [],
//             description: _t("Invalid date filter"),
//         };
//     }
//     let plusParam = null;
//     let selectedOptions;
//     try {
//         if (comparisonOptionId) {
//             [plusParam,selectedOptions] = getComparisonParams(referenceMoment, dateFilter, selectedOptionIds, comparisonOptionId);
//         } else {
//             selectedOptions = getSelectedOptions(referenceMoment, dateFilter, selectedOptionIds);
//         }
//     } catch (error) {
//         console.error("Error parsing selected options:", error);
//         return {
//             domain: dateFilter.domain || [],
//             description: _t("Error parsing options"),
//         };
//     }
//     if (selectedOptions && "withDomain"in selectedOptions && selectedOptions.withDomain.length > 0) {
//         const optionWithDomain = selectedOptions.withDomain[0];
//         const finalDomain = Domain.and([optionWithDomain.domain || [], dateFilter.domain || [], ]);
//         return {
//             description: optionWithDomain.description,
//             domain: finalDomain,
//         };
//     }
//     if (!selectedOptions || !selectedOptions.year) {
//         console.error("Parsed selectedOptions structure is unexpected or missing 'year':", selectedOptions);
//         return {
//             domain: dateFilter.domain || [],
//             description: _t("Invalid options structure"),
//         };
//     }
//     const yearOptions = selectedOptions.year || [];
//     const otherOptions = [...(selectedOptions.quarter || []), ...(selectedOptions.month || []), ];
//     try {
//         sortPeriodOptions(yearOptions);
//         sortPeriodOptions(otherOptions);
//     } catch (error) {
//         console.warn("Could not sort period options, proceeding without sort:", error);
//     }
//     const ranges = [];
//     for (const yearOption of yearOptions) {
//         if (!yearOption || !yearOption.setParam) {
//             console.warn("Skipping yearOption without setParam:", yearOption);
//             continue;
//         }
//         const constructRangeParams = {
//             referenceMoment,
//             fieldName,
//             fieldType,
//             plusParam,
//         };
//         if (otherOptions.length) {
//             for (const option of otherOptions) {
//                 if (!option || !option.setParam || !option.granularity) {
//                     console.warn("Skipping otherOption without setParam or granularity:", option);
//                     continue;
//                 }
//                 const setParam = {
//                     ...yearOption.setParam,
//                     ...option.setParam
//                 };
//                 const {granularity} = option;
//                 try {
//                     const range = jalaliConstructDateRange({
//                         ...constructRangeParams,
//                         granularity,
//                         setParam,
//                     });
//                     if (range && range.domain && typeof range.description !== "undefined") {
//                         ranges.push(range);
//                     } else {
//                         console.warn("jalaliConstructDateRange returned invalid result for:", {
//                             granularity,
//                             setParam
//                         });
//                     }
//                 } catch (error) {
//                     console.error("Error calling jalaliConstructDateRange:", error, {
//                         granularity,
//                         setParam,
//                     });
//                 }
//             }
//         } else {
//             if (!yearOption.granularity || !yearOption.setParam) {
//                 console.warn("Skipping yearOption without granularity or setParam:", yearOption);
//                 continue;
//             }
//             const {granularity, setParam} = yearOption;
//             try {
//                 const range = jalaliConstructDateRange({
//                     ...constructRangeParams,
//                     granularity,
//                     setParam,
//                 });
//                 if (range && range.domain && typeof range.description !== "undefined") {
//                     ranges.push(range);
//                 } else {
//                     console.warn("jalaliConstructDateRange returned invalid result for yearOption:", {
//                         granularity,
//                         setParam
//                     });
//                 }
//             } catch (error) {
//                 console.error("Error calling jalaliConstructDateRange for yearOption:", error, {
//                     granularity,
//                     setParam
//                 });
//             }
//         }
//     }
//     if (ranges.length === 0) {
//         console.warn("No valid date ranges generated for selected options.");
//         return {
//             domain: dateFilter.domain || [],
//             description: ""
//         };
//     }
//     let dateDomain = Domain.combine(ranges.map( (range) => range.domain), "OR");
//     const finalDomain = Domain.and([dateDomain, dateFilter.domain || []]);
//     const description = ranges.map( (range) => range.description).join(" / ");
//     return {
//         domain: finalDomain,
//         description
//     };
// }
   
// function jalaliConstructDateRange(params) {
//     const {referenceMoment, fieldName, fieldType, granularity, setParam, plusParam, } = params;
//     if ("quarter"in setParam) {
//         setParam.month = QUARTERS[setParam.quarter].coveredMonths[0];
//         delete setParam.quarter;
//     }
//     const date = referenceMoment.set(setParam).plus(plusParam || {});
//     const leftDate = jalaliStartOf(date, granularity);
//     const rightDate = jalaliEndOf(date, granularity);
//     let leftBound;
//     let rightBound;
//     if (fieldType === "date") {
//         leftBound = serializeDate(leftDate);
//         rightBound = serializeDate(rightDate);
//     } else {
//         leftBound = serializeDateTime(leftDate);
//         rightBound = serializeDateTime(rightDate);
//     }
//     const domain = new Domain(["&", [fieldName, ">=", leftBound], [fieldName, "<=", rightBound], ]);
//     const descriptions = [];
//     descriptions.push(date.toLocaleString("fa").split("/")[0]);
//     const method = localization.direction === "rtl" ? "push" : "unshift";
//     if (granularity === "month") {
//         if (method == "push") {
//             descriptions.push(JALALI_MONTH[parseInt(date.toLocaleString("fa").split("/")[1])]);
//         } else {
//             descriptions.unshift(JALALI_MONTH[parseInt(date.toLocaleString("fa").split("/")[1])]);
//         }
//     } else if (granularity === "quarter") {
//         const quarter = date.quarter;
//         if (method == "push") {
//             descriptions.push(QUARTERS[quarter].description.toString());
//         } else {
//             descriptions.unshift(QUARTERS[quarter].description.toString());
//         }
//     }
//     const description = descriptions.join(" ");
//     return {
//         domain,
//         description
//     };
// }
// function jalaliStartOf(date, granularity) {
//     try {
//         if (!toJalaali || !toGregorian) {
//             throw new Error("Jalali conversion functions (toJalaali/toGregorian) not available");
//         }
//         const sourceJDate = toJalaali(date.year, date.month, date.day);
//         if (!sourceJDate)
//             throw new Error("toJalaali failed to convert input date");
//         const jy = sourceJDate.jy;
//         const jm = sourceJDate.jm;
//         let targetJYear, targetJMonth, targetJDay;
//         switch (granularity) {
//         case "year":
//         case "years":
//             targetJYear = jy;
//             targetJMonth = 1;
//             targetJDay = 1;
//             break;
//         case "month":
//         case "months":
//             targetJYear = jy;
//             targetJMonth = jm;
//             targetJDay = 1;
//             break;
//         case "quarter":
//         case "quarters":
//             targetJYear = jy;
//             const jalaliQuarter = Math.ceil(jm / 3);
//             targetJMonth = (jalaliQuarter - 1) * 3 + 1;
//             targetJDay = 1;
//             break;
//         default:
//             return date.startOf(granularity);
//         }
//         const gDate = toGregorian(targetJYear, targetJMonth, targetJDay);
//         if (!gDate)
//             throw new Error("toGregorian failed for start date");
//         const startMoment = DateTime.fromObject({
//             year: gDate.gy,
//             month: gDate.gm,
//             day: gDate.gd
//         }, {
//             zone: date.zone
//         });
//         return startMoment.startOf("day");
//     } catch (e) {
//         console.error("Error in jalaliStartOf:", e, {
//             date: date.toString(),
//             granularity,
//         });
//         return date.startOf(granularity) || date.startOf("day");
//     }
// }
    
// function jalaliEndOf(date, granularity) {
//     try {
//         if (!toJalaali || !toGregorian || !jalaaliMonthLength) {
//             throw new Error("Jalali conversion/utility functions (toJalaali/toGregorian/jalaaliMonthLength) not available");
//         }
//         const sourceJDate = toJalaali(date.year, date.month, date.day);
//         if (!sourceJDate)
//             throw new Error("toJalaali failed to convert input date");
//         const jy = sourceJDate.jy;
//         const jm = sourceJDate.jm;
//         let targetJYear, targetJMonth, targetJDay;
//         switch (granularity) {
//         case "year":
//         case "years":
//             targetJYear = jy;
//             targetJMonth = 12;
//             targetJDay = jalaaliMonthLength(targetJYear, 12);
//             break;
//         case "month":
//         case "months":
//             targetJYear = jy;
//             targetJMonth = jm;
//             targetJDay = jalaaliMonthLength(targetJYear, targetJMonth);
//             break;
//         case "quarter":
//         case "quarters":
//             targetJYear = jy;
//             const jalaliQuarter = Math.ceil(jm / 3);
//             targetJMonth = jalaliQuarter * 3;
//             targetJDay = jalaaliMonthLength(targetJYear, targetJMonth);
//             break;
//         default:
//             return date.endOf(granularity);
//         }
//         const gDate = toGregorian(targetJYear, targetJMonth, targetJDay);
//         if (!gDate)
//             throw new Error("toGregorian failed for end date");
//         const endMoment = DateTime.fromObject({
//             year: gDate.gy,
//             month: gDate.gm,
//             day: gDate.gd
//         }, {
//             zone: date.zone
//         });
//         return endMoment.endOf("day");
//     } catch (e) {
//         console.error("Error in jalaliEndOf:", e, {
//             date: date.toString(),
//             granularity,
//         });
//         return date.endOf(granularity) || date.endOf("day");
//     }
// }





const isPersianUser = user.lang == "fa-IR";
if (isPersianUser) {
  function constructDateRange(params) {
    const { referenceMoment, fieldName, fieldType, granularity, setParam, plusParam } = params;
    let quarter 
    if ("quarter" in setParam) {
        // Luxon does not consider quarter key in setParam (like moment did)
        const jmonth = jDate(undefined,"persian",[+referenceMoment.toFormat('y'),
          QUARTERS[setParam.quarter].coveredMonths[0],
          +referenceMoment.toFormat('d'),
        ]).toCalendar("gregorian").month()
        setParam.month = jmonth;
        quarter = setParam.quarter;
        delete setParam.quarter;
    }
    let date = referenceMoment.set(setParam).plus(plusParam || {});
    if (quarter){
      if ([1, 2, 3].includes(date.month)){
      date = date.plus({year:1});
      }
    } 
    
    // compute domain
    const leftDate = JalaliStartOf(date, granularity)
    // const leftDate = date.startOf(granularity);
    const rightDate = JalaliEndOf(date, granularity)
    // const rightDate = date.endOf(granularity);
    let leftBound;
    let rightBound;
    if (fieldType === "date") {
        leftBound = serializeDate(leftDate);
        rightBound = serializeDate(rightDate);
    } else {
        leftBound = serializeDateTime(leftDate);
        rightBound = serializeDateTime(rightDate);
    }
    const domain = new Domain(["&", [fieldName, ">=", leftBound], [fieldName, "<=", rightBound]]);
    // compute description
    const descriptions = [date.toFormat("yyyy")];
    const method = localization.direction === "rtl" ? "push" : "unshift";
    if (granularity === "month") {
        descriptions[method](date.toFormat("MMMM"));
    } else if (granularity === "quarter") {
        const quarter = JALALI_MONTH_TO_RANGE[+date.toFormat("M")];
        descriptions[method](QUARTERS[quarter].description.toString());
    }
    const description = descriptions.join(" ");
    return { domain, description };
  }
  
  function constructDateDomain(referenceMoment, searchItem, selectedOptionIds, comparisonOptionId) {
    let plusParam;
    let selectedOptions;
    if (comparisonOptionId) {
      [plusParam, selectedOptions] = getComparisonParams(referenceMoment, searchItem, selectedOptionIds, comparisonOptionId);
    } else {
      selectedOptions = DatesUtils.getSelectedOptions(referenceMoment, searchItem, selectedOptionIds);
    }
    if ("withDomain" in selectedOptions) {
      return {
        description: selectedOptions.withDomain[0].description,
        domain: Domain.and([selectedOptions.withDomain[0].domain, searchItem.domain]),
      };
    }
    const yearOptions = selectedOptions.year;
    const otherOptions = [...(selectedOptions.quarter || []), ...(selectedOptions.month || [])];
    DatesUtils.sortPeriodOptions(yearOptions);
    DatesUtils.sortPeriodOptions(otherOptions);
    const ranges = [];
    const { fieldName, fieldType } = searchItem;
    for (const yearOption of yearOptions) {
      const constructRangeParams = {
        referenceMoment,
        fieldName,
        fieldType,
        plusParam,
      };
      if (otherOptions.length) {
        for (const option of otherOptions) {
          const setParam = Object.assign({}, yearOption.setParam, option ? option.setParam : {});
          const { granularity } = option;
          const range = constructDateRange(Object.assign({
            granularity,
            setParam
          }, constructRangeParams));
          ranges.push(range);
        }
      } else {
        const { granularity, setParam } = yearOption;
        const range = constructDateRange(Object.assign({
          granularity,
          setParam
        }, constructRangeParams));
        ranges.push(range);
      }
    }
    let domain = Domain.combine(ranges.map((range) => range.domain), "OR");
    domain = Domain.and([domain, searchItem.domain]);
    const description = ranges.map((range) => range.description).join("/");
    return {
      domain,
      description
    };
  }
  
  
  DatesUtils.constructDateRange = constructDateRange
  DatesUtils.constructDateDomain = constructDateDomain
  // DatesUtils.getPeriodOptions = jalaliGetPeriodOptions
}
// function getMonthPeriodOptions(referenceMoment, optionsParams) {
//     const { startYear, endYear, startMonth, endMonth } = optionsParams;
//     return [...Array(endMonth - startMonth + 1).keys()]
//         .map((i) => {
//             const monthOffset = startMonth + i;
//             const date = referenceMoment.plus({
//                 months: monthOffset,
//                 years: clamp(0, startYear, endYear),
//             });
//             const yearOffset = date.year - referenceMoment.year;
//             return {
//                 id: toGeneratorId("month", monthOffset),
//                 defaultYearId: toGeneratorId("year", clamp(yearOffset, startYear, endYear)),
//                 description: date.toFormat("MMMM"),
//                 granularity: "month",
//                 groupNumber: 1,
//                 plusParam: { months: monthOffset },
//             };
//         })
//         .reverse();
// }

// function getQuarterPeriodOptions(optionsParams) {
//     const { startYear, endYear } = optionsParams;
//     const defaultYearId = toGeneratorId("year", clamp(0, startYear, endYear));
//     return Object.values(QUARTER_OPTIONS).map((quarter) => ({
//         ...quarter,
//         defaultYearId,
//     }));
// }

// function getYearPeriodOptions(referenceMoment, optionsParams) {
//     const { startYear, endYear } = optionsParams;
//     return [...Array(endYear - startYear + 1).keys()]
//         .map((i) => {
//             const offset = startYear + i;
//             const date = referenceMoment.plus({ years: offset });
//             return {
//                 id: toGeneratorId("year", offset),
//                 description: date.toFormat("yyyy"),
//                 granularity: "year",
//                 groupNumber: 2,
//                 plusParam: { years: offset },
//             };
//         })
//         .reverse();
// }

// function getCustomPeriodOptions(optionsParams) {
//     const { customOptions } = optionsParams;
//     return customOptions.map((option) => ({
//         id: option.id,
//         description: option.description,
//         granularity: "withDomain",
//         groupNumber: 3,
//         domain: option.domain,
//     }));
// }




// function getSetParam(periodOption, referenceMoment) {
//     if (periodOption.granularity === "quarter") {
//         return periodOption.setParam;
//     }
//     const date = referenceMoment.plus(periodOption.plusParam);
//     const granularity = periodOption.granularity;
//     const setParam = { [granularity]: date[granularity] };
//     return setParam;
