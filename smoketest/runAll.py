import sys
import traceback
import os.path, time

from selenium.common.exceptions import NoSuchElementException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from smoketest.TestHelper import TestHelper
from smoketest.TestLog import TestLog
from smoketest.mylib.LoginHandler import LoginHandler
from smoketest.mylib.utils import Utils, GlobalFuncs
from smoketest.SmokeTest import SmokeTest
from optparse import OptionParser


def main():
    parser = OptionParser(usage="usage: %prog ipAddress browser logFileLocation")
    # parser.add_option("-c", "--chelp", help="Add arguments for IP Address for radio and target browser")
    (options, args) = parser.parse_args()
    # print('args', args)
    if len(args) != 3:
        parser.error("wrong number of arguments")

    GlobalFuncs.set_path(args[2])
    TEST_TYPE = 'smoketest'

    run_all = RunAll(TEST_TYPE)
    run_all.run_all()

    # try:
    #     run_all.run_all()
    # finally:
    #     Utils.print_tree(Utils.log_dir())

    # Utils.generate_overall_result(Utils.log_dir(), TEST_TYPE)


class RunAll:
    def __init__(self, test_type):
        self.test_type = test_type
        self.dir = Utils.log_dir()
        self.test_log = TestLog(self.dir)
        self.driver = Utils.create_driver(sys.argv[2])
        self.utils = Utils(self.driver, self.test_log)
        print('init')

    def run_all(self):

        self.run_smoke_test()

        # def doExpand(level):
        #     expanded = 0
        #     for each menu item at level
        #         if submenu:
        #             expand menu
        #             expanded++
        #     if expanded > 0:
        #         doExpand(level + 1)

    @classmethod
    def element_exists(cls, web_element, class_name):
        try:
            if web_element.find_element(By.CLASS_NAME, class_name):
                return True
        except NoSuchElementException as e:
            return False

    @staticmethod
    def do_expand(driver, level):
        expanded = 0
        list = []
        menu_items_by_level = driver.find_elements_by_xpath("//div[@aria-level='" + str(level) + "']")
        # menu_items_by_level = driver.find_elements_by_xpath("//a[@href='undefined']")

        for m in menu_items_by_level:

            menu_tree_row = m.find_element(By.CLASS_NAME, "menu-tree-row")

            if RunAll.element_exists(menu_tree_row, "menu-tree-collapsed-folder-icon"):
                m.click()
                time.sleep(1)
                expanded += 1
            elif RunAll.element_exists(menu_tree_row, "menu-tree-expanded-folder-icon"):
                expanded += 1
            else:
                list.append(m)

        if expanded > 0:
            sub_list = RunAll.do_expand(driver, level + 1)
            for i in sub_list:
                list.append(i)
        return list

    @staticmethod
    def make_path(el):
        res = []
        cur = el

        try:
            while cur:
                if cur.get_attribute('class') == "menu-tree-item":
                    try:
                        res.insert(0, cur.find_element(By.XPATH, "div[@class='menu-tree-row' or @class='menu-tree-row "
                                                                 "selected']").text)
                    except:
                        print "not found", cur

                cur = cur.find_element(By.XPATH, "..")
        except NoSuchElementException:
            return res

    @staticmethod
    def get_screens(driver):
        items_list = RunAll.do_expand(driver, 1)
        result = []

        for item in items_list:
            path = RunAll.make_path(item)
            # print path
            result.append(path)

        print result
        return result

    def run_smoke_test(self):
        # driver = Utils.create_driver(sys.argv[2])
        # utils = Utils(driver, self.test_log)
        self.utils.delete_existing_dir()

        self.test_log.start('login')
        test_helper = TestHelper(self.test_log, self.driver, self.test_type, self.utils)
        login_handler = LoginHandler(self.driver, test_helper, self.test_log)
        login_handler.start()

        # test_log = TestLog(self.dir)

        smoke_test = SmokeTest(self.driver, self.test_log, test_helper)
        try:
            side_menu = WebDriverWait(self.driver, 35).until(
                EC.presence_of_element_located((By.CLASS_NAME, "menu-tree-item")))
        except e:
            test_helper.assert_false(True, "unable to find side menu", "side_menu")
            login_handler.end()
            self.test_log.close()
            raise e

        # if you want to run individual tests
        # change smoke_test.create to take the parameters as a list

        # tests = RunAll.get_screens(self.driver)

        # smoke_test.create("Status/Equipment")
        smoke_test.create(["Status", "Alarms"])
        # smoke_test.create("Status/System Log")
        # smoke_test.create(["Status"]["Manufacturing Details"])
        # smoke_test.create("Status/ERPS")
        # smoke_test.create("Switching and Routing/Quality of Service/Classifiers")

        # smoke_test.create("System Configuration/Admin/Users")
        # smoke_test.create("Status/Manufacture Details")
        # smoke_test.create("Radio Configuration/Radio Links")
        # smoke_test.create("Switching & Routing Configuration/Port Manager")
        # smoke_test.create("Switching & Routing Configuration/Interfaces")

        # OR
        
        # if you want to run over all the screens, uncomment below
        tests = RunAll.get_screens(self.driver)

        # for test in tests:
        #     try:
        #         if not smoke_test.create(test):
        #             return False
        #     except Exception as ex:
        #         # error_file.write("Failed running: " + test + ex + '\r\n')
        #         print("Failed running ", test, ex)

        login_handler.end()
        self.test_log.close()


if __name__ == "__main__":

    count = 0
    # while 1:
    for x in xrange(1):
        # time.sleep(5)
        # main()
        try:
            time.sleep(5)
            main()
            count += 1
            print("Run " + str(count) + " times.")
        except Exception as e:
            import signal

            print("Main loop exception")

            traceback.print_exc()
            print("About to kill process: ", os.getpid())
            # os.kill(os.getpid(), signal.SIGBREAK)

    # main()
