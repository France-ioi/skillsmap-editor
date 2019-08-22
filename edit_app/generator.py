from .models import *
import os
import shutil
import re
from bs4 import BeautifulSoup
import sys

roots = Skill.objects.filter(name="root")

def get_path(skill):
   if not skill.parent:
      return ""
   path = skill.name
   skill = skill.parent
   while skill.parent:
      path = skill.name + "/" + path
      skill = skill.parent
   return path

def get_prerequisites(skill):
   paths = []
   for prerequisite in skill.prerequisites.all():
      paths.append("'" + get_path(prerequisite) + "'")
   return paths

def generate_tree(skill):
   tree = ""
   for child in skill.children.all():
      tree += "\"" + child.name + "\": " + generate_tree(child) + ","
   return "{" + tree + "}"

def gen_index(skill, base, depth):
   file = open(base + "/" + get_path(skill) + "/index.html", "w+")
   if skill.name != "root":
      file.write('\n'.join(
         ["<!DOCTYPE html>",
         "<html>",
         "<head>",
         "  <meta charset='utf-8'>",
         "  <title>" + skill.name + "</title>",
         "  <link class='task' type='text/css' rel='stylesheet' href='" + "../" * depth + "_common/modules/pemFioi/skill.css'>",
         "  <link class='task' type='text/css' rel='stylesheet'" + "../" * depth + "_common/modules/ext/bootstrap/css/bootstrap.min.css'>",
         "  <script class='remove' src='" + "../" * depth + "_common/modules/ext/requirejs/require.js'></script>",
         "  <script type='text/javascript'>",
         "    var modulesPath ='" + "../" * depth + "_common/modules';",
         "    var taskPlatformPath ='" + "../" * depth + "_common/task-platform';",
         "  </script>"
         "  <script type='text/javascript' src='" + "../" * depth + "_common/modules/pemFioi/skillConfig-1.0.js'></script>"
         "  <script type='text/javascript' class='remove'>",
         "    // general metadata conforming the PEM API Documentation for getMetaData",
         "    var PEMTaskMetaData = {",
         "      id: '" + get_path(skill) + "',",
         "      license: 'CC-BY-SA 3.0',",
         "      authors: [],",
         "      language: 'en',",
         "      difficulty: '',",
         "      prerequisites: [" + ','.join(get_prerequisites(skill)) + "],",
         "      relatedSkills: [],",
         "      augmentedSkills: []",
         "    };",
         "    var FIOITaskMetaData = {};",
         "  </script>",
         "</head>",
         "<body>",
         "  <div id='skillSummary'>",
         skill.abstract,
         "  </div>",
         "  <div id='resources'>",
         skill.resources,
         "  </div>",
         "  <div id='introductoryTasks'>",
         "  </div>",
         "</body>",
         "</html>"
         ]
      ))
   else:
      file.write('\n'.join(
         ["<html>",
          "<head>",
          "  <script src='../_common/modules/ext/jquery/2.1/jquery.min.js'></script>",
          "  <style>",
          "    a {",
          "      text-decoration:none",
          "    }",
          "  </style>",
          "</head>",
          "<body>",
          "  <div style='height:100%;width:360px;position:fixed;overflow:scroll' id='skillsList'></div>",
          "  <div style='height:100%;width:770px;position:fixed;left:370px;'>",
          "    <iframe style='width:99%;height:100%;padding:5px' id='skillContent'></iframe>",
          "  </div>",
          "</body>",
          "<script>",
          "var skills = ",
          generate_tree(skill),
          ";",
          "function display(branch, prefix, depth) {",
          "  var html = '';",
          "  for (var key in branch) {",
          "     var newPrefix = prefix.replace(' ', '%20') + key + '/';",
          "     var fontSize = Math.max(12, (40 - depth * 5));",
          "     html += \"<li><a href='#' onclick='openUrl(\\\"\" + newPrefix + \"index.html\\\")' style='font-size:\" + fontSize + \"px;'>\" + key + \"</a></li>\";",
          "     var subHtml = display(branch[key], newPrefix, depth + 1);",
          "     if (subHtml != '') {",
          "        html += '<ul>' + subHtml + '</ul>';",
          "     }",
          "  }",
          "  return html;",
          "}",
          "function openUrl(url) {",
          "  $('#skillContent').attr('src', url);",
          "}",
          "var html = display(skills, '', 1);",
          "$('#skillsList').html(html);",
          "</script>",
          "</html>"
         ]
      ))
   file.close()

def gen_skill(skill, base, depth):
   gen_index(skill, base, depth)
   for child in skill.children.all():
      os.mkdir(base + "/" + get_path(child))
      gen_skill(child, base, depth + 1)

def to_file_system(path):
   shutil.rmtree(path, ignore_errors=False, onerror=None)
   os.mkdir(path)
   gen_skill(roots[0], path, 1)

def get_from_path(path, root):
   names = path.split('/')
   
   cur_pos = root
   for skill_name in names:
      if skill_name == '':
         pass
      
      found = False
      for child in cur_pos.children.all():
         if child.name.lower() == skill_name.lower():
            cur_pos = child
            found = True
            break
         
      if not found:
         print("Error: " + path)
         return None
   
   return cur_pos

def parse_index(path, node, root):
   f = open(path, "r")
   text = f.read()
   soup = BeautifulSoup(text, 'lxml')
   
   reg_prerequisites = re.compile("prerequisites:(\s*?)\[(.*?)\],", re.DOTALL)
   
   node.abstract = str(soup.find(id="skillSummary").decode_contents(formatter="html"))
   node.resources = str(soup.find(id="resources").decode_contents(formatter="html") + "\n" + soup.find(id="introductoryTasks").decode_contents(formatter="html"))
   
   results = reg_prerequisites.search(text)
   if results:
      data = results.groups()[1]
      tab = eval("[" + data + "]")
      for prerequisite in tab:
         other = get_from_path(prerequisite, root)
         if other:
            node.prerequisites.add(other)
   node.save()

def parse_indexes(path, node, root):
   for folder in os.listdir(path):
      if not folder.startswith("index.html"):
         parse_indexes(path + "/" + folder, node.children.filter(name=str(folder))[0], root)
      elif folder == "index.html":
         parse_index(path + "/index.html", node, root) 

def gen_tree(path, node_name, node_parent):
   node = Skill(name = str(node_name), parent = node_parent)
   node.save()   
   for folder in os.listdir(path + "/" + node_name):
      if not folder.startswith("index.html"):
         gen_tree(path + "/" + node_name, folder, node)

#RUN IT ONLY ONE TIME, IT DROPS DATABASE !
def from_file_system(path):
   for task in Task.objects.all():
      task.delete()
   for folder in Folder.objects.all():
      if folder.name != "unsorted":
         folder.delete()
   for skill in Skill.objects.all():
      skill.delete()
   
   root = Skill(name="root", parent=None)
   root.save()
   
   for folder in os.listdir(path):
      if not folder.startswith("index.html"):
         gen_tree(path, folder, root)
   
   for folder in os.listdir(path):
      if not folder.startswith("index.html"):
         parse_indexes(path + "/" + str(folder), root.children.filter(name=str(folder))[0], root)
