/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";

const{ useState } = owl;

class StudentListController extends ListController {
  setup() {
    super.setup();

    // Services used in the controller
    this.orm = useService("orm");
    this.action = useService("action");

    // Initializing the reactive state
    this.state = useState({
      studentOrgs: [],
      activeOrgId: null,
      selectedView: "all",
      currentPage: 1,
      itemsPerPage: 3,
    });

    // Binding methods to ensure 'this' context
    this.allOrgs = []; // Used to store the full list of organizations
    this.goToPage = this.goToPage.bind(this);
    this.selectOrgs = this.selectOrgs.bind(this);
    this.onDropdownChange = this.onDropdownChange.bind(this);
    this.searchOrganization = this.searchOrganization.bind(this);
    this.changeItemsPerPage = this.changeItemsPerPage.bind(this);


    // Fetch initial data
    this.initializeData();
  }

  async initializeData() {
    try {
      const allOrgs = await this.orm.readGroup(
        "portal.student",
        [],
        ["student_organization_student_ids"],
        ["student_organization_student_ids"]
      );

      this.state.studentOrgs = allOrgs.slice(0, -1); // Exclude the last item for individual count
      this.allOrgs = allOrgs.slice(0, -1);
      this.state.totalOrgs = this.state.studentOrgs.length;
      this.state.totalStudents = allOrgs.reduce((sum, org) => sum + org.student_organization_student_ids_count, 0);
      this.state.totalIndividualStudents = allOrgs[allOrgs.length - 1].student_organization_student_ids_count;
      this.state.totalBusinessStudents = this.state.totalStudents - this.state.totalIndividualStudents;
    } catch (error) {
      console.error(error);
    }
  }

  paginatedOrgs() {
    const start = (this.state.currentPage - 1) * this.state.itemsPerPage;
    const end = start + this.state.itemsPerPage;
    return this.state.studentOrgs.slice(start, end);
  }

  goToPage(page) {
    this.state.currentPage = page;
  }

  selectOrgs(org) {
    const [id, name] = org;
    this.state.activeOrgId = id;
    this.state.selectedView = "business";

    this.env.searchModel.setDomainParts({
      org: {
        domain: [["student_organization_student_ids", "=", id]],
        facetLabel: name,
      },
    });
  }

  selectAllStudents() {
    this.state.selectedView = "all";
    this.state.activeOrgId = null;
    this.state.studentOrgs = [...this.allOrgs];
    this.env.searchModel.setDomainParts({ org: { domain: [], facetLabel: "All Students" } });
  }

  selectIndividualView() {
    this.state.selectedView = "individual";
    this.state.activeOrgId = null;
    this.env.searchModel.setDomainParts({ org: { domain: [["student_organization_student_ids", "=", null]], facetLabel: "Individual" } });
  }

  selectBusinessView() {
    this.state.selectedView = 'business';
    this.state.activeOrgId = null;
    this.env.searchModel.setDomainParts({ org: { domain: [["student_organization_student_ids", "!=", null]], facetLabel: "Business" } });
  }

  onDropdownChange(event) {
    const selectedValue = event.target.value;
    switch (selectedValue) {
      case 'individual':
        this.selectIndividualView();
        break;
      case 'business':
        this.selectBusinessView();
        break;
      default:
        this.selectAllStudents();
    }
  }

  changeItemsPerPage(newLimit) {
    this.state.itemsPerPage = parseInt(newLimit, 10);
    this.state.currentPage = 1; // Reset to the first page
  }


  searchOrganization(event) {
    const searchTerm = event.target.value.toLowerCase();

    // Apply the search filter or reset to the full list
    this.state.studentOrgs = searchTerm ?
      this.allOrgs.filter(org =>
        org.student_organization_student_ids[1].toLowerCase().includes(searchTerm)
      ) :
      [...this.allOrgs];

    // If the search term is cleared and there is a selected organization
    if (!searchTerm && this.state.activeOrgId !== null) {
      // Find the index of the selected organization
      const selectedIndex = this.state.studentOrgs.findIndex(
        org => org.student_organization_student_ids[0] === this.state.activeOrgId
      );

      // Calculate the page number
      if (selectedIndex !== -1) {
        const pageNumber = Math.ceil((selectedIndex + 1) / this.state.itemsPerPage);
        this.state.currentPage = pageNumber;
      }
    } else {
      // Reset to the first page when a new search is performed or search is cleared without selection
      this.state.currentPage = 1;
    }
  }

}

StudentListController.template = "owl.StudentListView";

export const studentListView = {
  ...listView,
  Controller: StudentListController,
};

registry.category("views").add("owl_student_list_view", studentListView);
