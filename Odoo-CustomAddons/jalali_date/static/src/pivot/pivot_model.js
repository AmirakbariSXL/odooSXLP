import { PivotModel } from "@web/views/pivot/pivot_model";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
const isPersianUser = user.lang == "fa-IR";
if (isPersianUser) {
  patch(PivotModel.prototype,{
   _getGroupLabels(group, groupBys, config) {
     console.log("group", group);
    return groupBys.map((gb) => {
      const groupBy = this._normalize(gb);
        return this._sanitizeLabel(group[groupBy], groupBy, config);
    });
    }
  });
}
