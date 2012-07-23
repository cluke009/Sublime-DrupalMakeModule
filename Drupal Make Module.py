import os, textwrap
import sublime, sublime_plugin


class DrupalMakeModuleCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.count = 0
        self.window = self.view.window()
        self.root = self.get_root()
        self.show_filename_input()

    def get_root(self):
        try:
            root = self.window.folders()[0]
        except IndexError:
            root = os.path.abspath(os.path.dirname(self.view.file_name()))
        return root

    def show_filename_input(self, initial='sites/all/modules'):
        caption = 'Drupal Module Path'
        self.window.show_input_panel(
            caption, initial,
            self.entered_filename, '', None
        )

    def entered_filename(self, filename):
        file_path = os.path.join(self.root, filename)
        file_path = os.path.abspath(file_path)
        base, filename = os.path.split(filename)

        if not os.path.exists(file_path):
            self.create(file_path)

        file_dir = file_path + "/" + filename

        if not os.path.exists(file_dir + '.module'):
            moduleText = textwrap.dedent('''\
                <?php
                /**
                 * @file
                 */

                /**
                 * Implements hook_help().
                 */
                function ''' + filename + '''_help($path, $arg) {
                  global $base_url;

                  switch ($path) {
                    case 'admin/help#''' + filename + '''\':
                      $output = '<p>'. t('') .'</p>';
                      break;
                  }
                  return $output;
                }

                /**
                 * Implements hook_perm()
                 * @return array An array of valid permissions
                 */
                function ''' + filename + '''_perm() {
                  return array('access ''' + filename + ''' content');
                }
            ''')
            MODULE = open(file_dir + '.module', 'w')
            MODULE.writelines(moduleText)
            MODULE.close()

        if not os.path.exists(file_dir + '.install'):
            installText = textwrap.dedent('''\
                <?php
                /**
                 * Implements hook_schema().
                 */
                function ''' + filename + '''_schema() {
                  $schema['mytable1'] = array(
                     // specification for mytable1
                  );
                  return $schema;
                }

                /**
                 * Implements hook_install().
                 */
                function ''' + filename + '''_install() {
                  // Create my tables.
                  drupal_install_schema(\'''' + filename + '''\');
                }

                /**
                 * Implements hook_uninstall().
                 */
                function ''' + filename + '''_uninstall() {
                  // Drop my tables.
                  drupal_uninstall_schema(\'''' + filename + '''\');
                }
            ''')
            INSTALL = open(file_dir + '.install', 'w')
            INSTALL.writelines(installText)
            INSTALL.close()

        if not os.path.exists(file_dir + '.info'):
            infoText = textwrap.dedent('''\
                name = ''' + filename + '''
                description =
                core = 6.x
                package =
                php =
                version =
                dependencies[] =
            ''')
            INFO = open(file_dir + '.info', 'w')
            INFO.writelines(infoText)
            INFO.close()

    def create(self, filename):
        base, filename = os.path.split(filename)
        self.create_folder(base + "/" + filename)

    def create_folder(self, base):
        if not os.path.exists(base):
            parent = os.path.split(base)[0]
            if not os.path.exists(parent):
                self.create_folder(parent)
            os.mkdir(base)
