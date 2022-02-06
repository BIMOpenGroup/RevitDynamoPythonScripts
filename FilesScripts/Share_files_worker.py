# -*- coding: utf-8 -*-
# region -----------------------Libary import----------------------
import clr
import sys
sys.path.append(u'C:\\Program Files (x86)\\IronPython 2.7\\Lib')
sys.path.append(u'C:\\libs')
import os
import shutil
import glob
import traceback
import json
import inspect
import gc  # garbage collector
import ctypes
import collections
# import shutil

clr.AddReference('Win32Api')
from Win32Api import Win32Api

import System
from System import Guid, DateTime, Type, Text, IO, Threading, Convert
from System.IO import StreamReader, File, Directory, FileStream
from System.Net import WebRequest
from System.Collections.Generic import List

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Viewport
from Autodesk.Revit.ApplicationServices import ControlledApplication
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Events import *
from Autodesk.Revit.DB.Events import *

from Autodesk.Revit.Creation import ItemFactoryBase

clr.AddReference("RevitServices")
# import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
path_to_new_folder_file = 'C:/RS_logs/'
log_file_name = 'SharedFiles.log'
path_to_log_file = "{}{}".format(path_to_new_folder_file, log_file_name)
try:
	if not Directory.Exists(path_to_new_folder_file):
		Directory.CreateDirectory(path_to_new_folder_file)
except:  # noqa
	pass

# endregion -----------------------Libary import----------------------


# region -----------------------helpers----------------------
class TimeCounter:
	def __init__(self):
		self.time = Stopwatch.StartNew()
		self.time.Start()

	def stop(self):
		self.time.Stop()
		time = self.time.Elapsed
		return ":".join([str(i) for i in [time.Minutes, time.Seconds, time.Milliseconds]])


def LogSave(info):
	try:
		if info:
			string_list_info = []
			string_list_info.append("")
			string_list_info.append(DateTime.Now.ToLocalTime().ToString())
			if isinstance(info, list):
				for i in info:
					string_list_info.append(i)
			else:
				string_list_info.append(info)
			IO.File.AppendAllLines(path_to_log_file, string_list_info, Text.Encoding.Unicode)
	except: # noqa
		pass
# endregion -----------------------helpers----------------------


# region -----------------------IFailuresProcessor and DialogBoxShowing_off----------------------
def UiAppOnDialogBoxShowing(sender_uiapp, args):
	activ_doc = sender_uiapp.ActiveUIDocument.Document
	activ_doc_name = "none"
	if activ_doc is not None:
		activ_doc_name = activ_doc.Title
	LogSave(["UiAppOnDialogBoxShowing:", "activ_doc.Title: {}".format(activ_doc_name), "args Type: {}".format(args.GetType().ToString()), "args.DialogId: {}".format(args.DialogId)])
	if args.GetType() == TaskDialogShowingEventArgs:
		if (args.DialogId == "TaskDialog_File_Name_In_Use"):
			args.OverrideResult(1001)
		elif(args.DialogId == "TaskDialog_Unresolved_References"):
			args.OverrideResult(1002)
		elif(args.DialogId == "TaskDialog_Changes_Not_Saved"):
			args.OverrideResult(1001)
		elif(args.DialogId == "TaskDialog_Missing_Third_Party_Updaters"):
			args.OverrideResult(1001)
		else:
			args.OverrideResult(1001)
	elif args.GetType() == DialogBoxShowingEventArgs:
		if args.DialogId == "Dialog_Revit_PartitionsSaveToMaster":
			args.OverrideResult(1)
		if args.DialogId == "Dialog_Revit_DocWarnDialog":
			LogSave(["Win32Api.ClickOk()"])
		else:
			args.OverrideResult(1)
	else:
		LogSave(["UiAppOnDialogBoxShowing else args.OverrideResult(1)"])
		args.OverrideResult(1)
	Win32Api.ClickOk()


def FailureResolutionTypes():
	fail_res_types = []
	fail_res_types.append(FailureResolutionType.Invalid)
	fail_res_types.append(FailureResolutionType.Default)
	fail_res_types.append(FailureResolutionType.CreateElements)
	fail_res_types.append(FailureResolutionType.DeleteElements)
	fail_res_types.append(FailureResolutionType.SkipElements)
	fail_res_types.append(FailureResolutionType.MoveElements)
	fail_res_types.append(FailureResolutionType.FixElements)
	fail_res_types.append(FailureResolutionType.DetachElements)
	fail_res_types.append(FailureResolutionType.QuitEditMode)
	fail_res_types.append(FailureResolutionType.UnlockConstraints)
	fail_res_types.append(FailureResolutionType.SetValue)
	fail_res_types.append(FailureResolutionType.SaveDocument)
	fail_res_types.append(FailureResolutionType.ShowElements)
	fail_res_types.append(FailureResolutionType.Others)
	return fail_res_types


def FailListDict():
	clr_binf_type = clr.GetClrType(BuiltInFailures)  # BINGO
	clr_list_of_binf_fails = clr_binf_type.GetNestedTypes()
	# Словарь BuiltInFailures где key: имя класса ошибки + свойство ошибки; value: FailureDefinitionId
	dict_binf_and_id = {"{0}.{1}".format(binf.FullName.replace("+", "."), binfprop.Name): binfprop.GetGetMethod().Invoke(binf, None) for binf in clr_list_of_binf_fails for binfprop in binf.GetProperties()}
	return dict_binf_and_id


def fail_stat(fail_m):
	result = []
	ad_ids = [eid.IntegerValue for eid in fail_m.GetAdditionalElementIds()]
	fail_ids = [eid.IntegerValue for eid in fail_m.GetFailingElementIds()]
	has_res_of_type = ["{0} = {1}".format(str(res_type), str(fail_m.HasResolutionOfType(res_type))) for res_type in FailureResolutionTypes() if fail_m.HasResolutionOfType(res_type)]
	result.append("***")
	result.append(fail_m.HasResolutions())  # 0
	result.append("FailureType = {0}".format(fail_m.GetSeverity()))  # 1
	result.append(fail_m.GetDescriptionText())  # 2
	result.append(fail_m.GetDefaultResolutionCaption())  # 3
	if fail_m.HasResolutions():
		result.append("CurrentResolutionType = {}".format(fail_m.GetCurrentResolutionType()))  # 4
	else:
		result.append("CurrentResolutionType = {}".format("does not have any resolutions"))
	result.append(fail_m.GetNumberOfResolutions())  # 5
	result.append(fail_m.GetFailureDefinitionId().Guid)
	result.append("AdditionalElementIds: {}".format(ad_ids))  # 7
	result.append("FailingElementIds: {}".format(fail_ids))  # 8
	result.append(has_res_of_type)  # 9
	result.append([(item[0], str(item[1].Guid.ToString())) for item in FailListDict().items() if item[1] == fail_m.GetFailureDefinitionId()])
	result.append("***")
	string_list = [str(r) for r in result]
	return string_list


class WarningSwallower_BC(IFailuresProcessor):
	def ProcessFailures(self, failuresAccessor):
		try:
			failuresAccessor.DeleteAllWarnings()
			fh_options = failuresAccessor.GetFailureHandlingOptions()
			fh_options.SetClearAfterRollback(True)
			failuresAccessor.SetFailureHandlingOptions(fh_options)
			fail_messages = failuresAccessor.GetFailureMessages()
			for fail_m in fail_messages:
				info = fail_stat(fail_m)
				LogSave(info)
				try:
					if fail_m.GetSeverity() != FailureSeverity.Warning:
						if fail_m.HasResolutions():
							failuresAccessor.ResolveFailure(fail_m)
					else:
						failuresAccessor.DeleteWarning(fail_m)
				except Exception as e:
					tb2 = sys.exc_info()[2]
					line = tb2.tb_lineno
					LogSave(["[0 IFailuresProcessor iteration]: Code error on line {0} Has failure {1} \n {2}".format(str(line), str(e), fail_m.GetDescriptionText())])
			return FailureProcessingResult.ProceedWithCommit
		except Exception as e:
			tb2 = sys.exc_info()[2]
			line = tb2.tb_lineno
			LogSave(["[1 IFailuresProcessor main def]: Code error on line {0} Has failure {1} \n {2}".format(str(line), str(e), fail_m.GetDescriptionText())])
			return FailureProcessingResult.ProceedWithRollBack

	def Dismiss(self, current_doc):
		pass
# endregion -----------------------IFailuresProcessor and DialogBoxShowing_off----------------------


# region -----------------------Open Save options----------------------
opn_opt = OpenOptions()
opn_opt.Audit = True
opn_opt.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
workset_config = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
opn_opt.SetOpenWorksetsConfiguration(workset_config)


sv_as_opt = SaveAsOptions()
sv_as_opt.Compact = True
sv_as_opt.OverwriteExistingFile = True

wrksh_svas_opt = WorksharingSaveAsOptions()
wrksh_svas_opt.SaveAsCentral = True
# wrksh_svas_opt.ClearTransmitted = True
sv_as_opt_work_shared = SaveAsOptions()
sv_as_opt_work_shared.Compact = True
sv_as_opt_work_shared.OverwriteExistingFile = True
sv_as_opt_work_shared.SetWorksharingOptions(wrksh_svas_opt)
# endregion -----------------------Open Save options----------------------


# region -----------------------Revit api----------------------
def links_off(new_mpath):
	data = TransmissionData.ReadTransmissionData(new_mpath)
	files_refs_ids = data.GetAllExternalFileReferenceIds()
	links_count = 0
	for file_ref_id in files_refs_ids:
		file_ref = data.GetLastSavedReferenceData(file_ref_id)
		if file_ref.ExternalFileReferenceType == ExternalFileReferenceType.RevitLink:
			try:
				mpath_link = file_ref.GetPath()
				path_type = file_ref.PathType
				data.SetDesiredReferenceData(file_ref_id, mpath_link, path_type, False)
				data.IsTransmitted = True
				TransmissionData.WriteTransmissionData(new_mpath, data)
				links_count += 1
			except Exception as e:
				tb2 = sys.exc_info()[2]
				line = tb2.tb_lineno
				LogSave(["links_off {0} Has failure {1}".format(str(line), str(e))])
	data.Dispose()
	return links_count


def save_Performance_Adviser_Rules():
	adviser = PerformanceAdviser.GetPerformanceAdviser()
	ruleIds = adviser.GetAllRuleIds()
	# rules_count = adviser.GetNumberOfRules()
	rule_info = []
	rule_info_log = "(ruleId, name, desc, enabled, check)"
	rule_info.append(rule_info_log)
	# for index in range(0, rules_count):
	for ruleId in ruleIds:
		name = adviser.GetRuleName(ruleId)
		desc = adviser.GetRuleDescription(ruleId)
		enabled = adviser.IsRuleEnabled(ruleId)
		check = adviser.WillRuleCheckElements(ruleId)
		LogSave(["Performance_Adviser_Rule", rule_info_log, str(ruleId.Guid), name, desc, str(enabled), str(check)])
		rule_info.append((str(ruleId.Guid), name, desc, str(enabled), str(check)))
	return rule_info


def shared_files_worker(file_names_and_paths_dict, new_folder, view_prifix):
	date = DateTime.Today.ToString("d").split(".")
	date_revers = "{}.{}.{}".format(date[2], date[1], date[0])
	new_path_date = "{}/{}".format(new_folder, date_revers)
	if not os.path.exists(new_path_date):
		os.makedirs(new_path_date)
	for file_name, file_path in file_names_and_paths_dict.items():
		try:
			mpatch = ModelPathUtils.ConvertUserVisiblePathToModelPath(file_path)

			new_path = "{}\\{}".format(new_path_date, file_name)
			LogSave(["SHARED file path", new_path])
			app.CopyModel(mpatch, new_path, True)

			new_model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(new_path)
			links_off(new_model_path)

			basic_file_info = BasicFileInfo.Extract(new_path)
			is_work_shared = basic_file_info.IsWorkshared
			saved_doc = app.OpenDocumentFile(new_model_path, opn_opt)

			PurgeGuid = "e8c63650-70b7-435a-9010-ec97660c1bda"
			PurgeRuleId = List[PerformanceAdviserRuleId]()

			adviser = PerformanceAdviser.GetPerformanceAdviser()
			ruleIds = adviser.GetAllRuleIds()

			for ruleId in ruleIds:
				if str(ruleId.Guid) == PurgeGuid:
					PurgeRuleId.Add(ruleId)
					continue

			failureMessages = adviser.ExecuteRules(saved_doc, PurgeRuleId)
			purgeableElements = []
			# view_prifix = ["20", "30"]
			trans2 = Transaction(saved_doc, 'Create new SHARED file')
			trans2.Start()
			try:
				# VIEWER_SHEET_NUMBER
				# param_id = ElementId(BuiltInParameter.VIEWER_SHEET_NUMBER)
				# # pvp = ParameterValueProvider(param_id)
				# # fsr = FilterStringEquals()
				# # # has_no_param_value = HasNoValueFilterRule(param_id)
				# # # param_filter = ElementParameterFilter(has_no_param_value)
				# # fRule = FilterStringRule(pvp, fsr, "---", True)
				# # view_sheet_number_param_filter = ElementParameterFilter(fRule)

				all_view_sheet_ids = FilteredElementCollector(saved_doc).OfClass(ViewSheet).ToElementIds()
				all_sche_shee_insts = FilteredElementCollector(saved_doc).OfClass(ScheduleSheetInstance).ToElements()
				all_viewport = FilteredElementCollector(saved_doc).OfClass(Viewport).ToElements()

				all_sche_shee_insts_ids = List[ElementId]()
				all_viewport_ids = List[ElementId]()
				[all_sche_shee_insts_ids.Add(schedule_sheet.ScheduleId) for schedule_sheet in all_sche_shee_insts]
				[all_viewport_ids.Add(viewport.ViewId) for viewport in all_viewport]

				all_ids_to_exclude = List[ElementId]()
				all_ids_to_exclude.AddRange(all_sche_shee_insts_ids)
				all_ids_to_exclude.AddRange(all_viewport_ids)
				all_ids_to_exclude.AddRange(all_view_sheet_ids)
				all_filters = ExclusionFilter(all_ids_to_exclude)

				# sche_shee_insts_filter = ExclusionFilter(all_sche_shee_insts_ids)
				# viewport_filter = ExclusionFilter(all_viewport_ids)
				# sheet_filter = ExclusionFilter(all_view_sheet_ids)

				# all_filters = LogicalAndFilter([sche_shee_insts_filter, viewport_filter, sheet_filter])

				all_views = FilteredElementCollector(saved_doc).OfClass(View).WherePasses(all_filters).ToElements()
				LogSave(["all_views, all_sche_shee_insts_ids, all_viewport_ids len:", str(len(all_views)), str(len(all_sche_shee_insts_ids)), str(len(all_viewport_ids))])
				del all_views[-1]
				if len(failureMessages) > 0:
					purgeableElements = failureMessages[0].GetFailingElements()
					saved_doc.Delete(purgeableElements)
				if len(all_views) > 0:
					for view in all_views:
						if view:
							view_name = "--can't get View Name--"
							view_id = "--can't get View Id--"
							try:
								view_id = view.Id.IntegerValue
								view_name = view.Name
								split_view_name = view_name.split("_")
								if len(split_view_name) > 0 and split_view_name[0] not in view_prifix:
									saved_doc.Delete(view.Id)
							except Exception as e:
								tb2 = sys.exc_info()[2]
								line = tb2.tb_lineno
								LogSave(["fils_shared_from_rsn [0]: line {} failure {} \n Can't delete view {} \n its name [ {} ] \n id [ {} ]".format(str(line), str(e), str(view), view_name, view_id)])

			except Exception as e:
				tb2 = sys.exc_info()[2]
				line = tb2.tb_lineno
				LogSave(["fils_shared_from_rsn [1]: Code error on line {0} Has failure {1}".format(str(line), str(e))])
			trans2.Commit()
			if is_work_shared:
				saved_doc.SaveAs(new_model_path, sv_as_opt_work_shared)
			else:
				saved_doc.SaveAs(new_model_path, sv_as_opt)
			saved_doc.Close(False)
			LogSave(["All OK shared file", new_path, "saved"])
		except Exception as e:
			tb2 = sys.exc_info()[2]
			line = tb2.tb_lineno
			LogSave(["fils_shared_from_rsn [2]: Code error on line {0} Has failure {1}".format(str(line), str(e))])
# endregion -----------------------Revit api----------------------


# region -----------------------Revit api parameters----------------------
app = DocumentManager.Instance.CurrentUIApplication.Application
uiapp = DocumentManager.Instance.CurrentUIApplication
version = app.VersionNumber
current_doc = DocumentManager.Instance.CurrentDBDocument
view = current_doc.ActiveView
# endregion -----------------------Revit api parameters----------------------


# region -----------------------Dynamo parameters----------------------
from_folder = IN[0]  # noqa
to_shared_folder = IN[1]  # noqa
view_prifix = IN[2]  # noqa
run_mode = IN[3]  # noqa
# endregion -----------------------Dynamo parameters----------------------


# region -----------------------main----------------------
if run_mode:
	rule_info = save_Performance_Adviser_Rules()
	OUT = "Performance_Adviser_Rule:", rule_info
else:
	app.RegisterFailuresProcessor(WarningSwallower_BC())
	uiapp.DialogBoxShowing += UiAppOnDialogBoxShowing

	# names = os.listdir(from_folder)
	file_paths_to_shared = glob.glob(from_folder + "\\*.rvt")
	file_names_and_paths_dict = {path.split("\\")[-1]: path for path in file_paths_to_shared}

	shared_files_worker(file_names_and_paths_dict, to_shared_folder, view_prifix)

	uiapp.DialogBoxShowing -= UiAppOnDialogBoxShowing

	OUT = "Структура выбранной папки:", file_names_and_paths_dict
# endregion -----------------------main----------------------
