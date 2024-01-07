/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

const { onWillStart, useState } = owl;

class StudentListController extends ListController {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.action = useService("action");
    this.allOrgs = [];
    this.totalOrgs = 0;
    this.totalStudents = 0;
    this.totalIndividualStudents = 0;
    this.totalBusinessStudents = 0;
    this.state = useState({
      studentOrgs: [],
      activeOrgId: null,
      selectedView: "all",
      currentPage: 1,
      itemsPerPage: 3,
    });
    this.goToPage = (page) => {
      this.state.currentPage = page;
    };

    this.selectOrgs = (org) => {
      const id = org[0];
      const name = org[1];
      this.state.activeOrgId = id;
      this.state.selectedView = "business";

      console.log("Selected Org Id::", id);
      console.log("Selected Org::", name);

      this.env.searchModel.setDomainParts({
        org: {
          domain: [["student_organization_student_ids", "=", id]],
          facetLabel: name,
        },
      });
    };

    onWillStart(async () => {
      const allOrgs = await this.orm.readGroup(
        "portal.student",
        [],
        ["student_organization_student_ids"],
        ["student_organization_student_ids"]
      );
      this.allOrgs = allOrgs;
      for (let i = 0; i < this.allOrgs.length; i++) {
        this.totalStudents += this.allOrgs[i].student_organization_student_ids_count;
      }
      this.totalIndividualStudents = this.allOrgs[this.allOrgs.length - 1].student_organization_student_ids_count;
      this.totalBusinessStudents = this.totalStudents - this.totalIndividualStudents;
      allOrgs.pop(); 
      this.totalOrgs = this.allOrgs.length;
      this.state.studentOrgs = [...this.allOrgs]; 
    });
  }

  paginatedOrgs() {
    const start = (this.state.currentPage - 1) * this.state.itemsPerPage;
    const end = start + this.state.itemsPerPage;
    return this.state.studentOrgs.slice(start, end);
  }


  selectAllStudents() {
    console.log("selecte All Students");
    this.state.selectedView = "all";
    this.state.activeOrgId = null;
    this.env.searchModel.setDomainParts({
      org: {
        domain: [],
        facetLabel: "All Students",
      },
    });
    this.state.activaOrgId = null;
  }

  selectIndividualView() {
    console.log("selecte Individual View");
    this.state.selectedView = "individual";
    this.state.activeOrgId = null;
    this.env.searchModel.setDomainParts({
      org: {
        domain: [["student_organization_student_ids", "=", null]],
        facetLabel: "Individual",
      },
    });
  }

  selectBusinessView() {
    this.state.selectedView = 'business'
    this.state.activeOrgId = null;
    console.log("selecte Business View");
    this.env.searchModel.setDomainParts({
      org: {
        domain: [["student_organization_student_ids", "!=", null]],
        facetLabel: "Business",
      },
    });
  }

  selectOrgs(org) {
    console.log('Called')
    const id = org[0];
    const name = org[1];
    console.log("Selected Org Id::", id);
    console.log("Selected Org::", name);
    this.state.activeOrgId = id;
    this.state.selectedView = "business";

    console.log("Selected Org Id::", id);
    console.log("Selected Org::", name);

    this.env.searchModel.setDomainParts({
      org: {
        domain: [["student_organization_student_ids", "=", id]],
        facetLabel: name,
      },
    });

  }

  onDropdownChange(event) {
    const selectedValue = event.target.value;
    if (selectedValue === 'individual') {
      this.selectIndividualView();
    } else if (selectedValue === 'business') {
      this.selectBusinessView();
    } else {
      this.selectAllStudents();
    }

  
}

searchOrganization(event) {
  const searchTerm = event.target.value.toLowerCase();
  if (searchTerm) {
    const searchResult = this.allOrgs.filter(org =>
      org.student_organization_student_ids[1].toLowerCase().includes(searchTerm)
    );
    this.state.studentOrgs = searchResult;
  } else {
    this.state.studentOrgs = [...this.allOrgs]; 
  }
}

}



StudentListController.template = "owl.StudentListView";

export const studentListView = {
  ...listView,
  Controller: StudentListController,
};

registry.category("views").add("owl_student_list_view", studentListView);
