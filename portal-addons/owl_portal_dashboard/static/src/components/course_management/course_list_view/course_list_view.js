/** @odoo-module */

import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { ListController } from '@web/views/list/list_controller';
import { useService } from '@web/core/utils/hooks';

const { onWillStart, useState, useRef } = owl;

class CourseListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.action = useService('action');
        this.allPOLPs = [];
        this.totalPOLPs = 0;
        this.state = useState({
            coursePOLPs: [],
            activePOLPId: null,
        });
        onWillStart(
            async() => {
                const allPOLPs = await this.orm.readGroup(
                    "course_management",
                    [],
                    ['po_learning_program_ids'],
                    ['po_learning_program_ids']
                )
                this.allPOLPs = allPOLPs;
                console.log("allPOLPs", this.allPOLPs);
            }
            
        )
    }

}

CourseListController.template = 'owl.CourseListView';

export const courseListView = {
    ...listView,
    Controller: CourseListController,
}

registry.category("views").add("owl_course_list_view", courseListView);