		def lookp(element,param,value): #value "s"=AsString(),"i"=AsInteger(),"d"=AsDouble()
			if value == "s":
				out = element.LookupParameter(param).AsString()
			elif value == "i":
				out = element.LookupParameter(param).AsInteger()
			elif value == "d":
				out = element.LookupParameter(param).AsDouble()
			else:
				out = "NOT ENAF MINERALS"
			return out
			
		def lookps(element,param): #value "s"=AsString(),"i"=AsInteger(),"d"=AsDouble()
			return element.LookupParameter(param).AsString()
		
		def lookp_r_typ_str(element):
			return element.LookupParameter("BS_Тип квартиры").AsString()#("ROM_Тип квартиры").AsString()

			
#-----------------------Первое правило------------------------------------------------------------------
		provider_area_param = ParameterValueProvider(ElementId(BuiltInParameter.ROOM_AREA))
		filt_great = FilterNumericGreater()
		f_are_rule = FilterDoubleRule(provider_area_param,filt_great,0,1E-6)

#-----------------------Второе правило------------------------------------------------------------------	
		"""
		iterator = doc.ParameterBindings.ForwardIterator()
		rom_zon_param_id = None
		while iterator.MoveNext():
			test.append(iterator.Key)
			if iterator.Key.Name == "ROM_Зона":
				rom_zon_param_id = iterator.Key.Id
		#provider_zoon_param = ParameterValueProvider(rom_zon_param_id)
		"""	
		from System import Guid
		#from System import Type
		from System.Collections.Generic import List
		#from System.Reflection import *
		
		sh_par_el = FilteredElementCollector(doc).OfClass(SharedParameterElement)
		rom_zon_param_id = -1
		for e in sh_par_el:
			if e.GetDefinition().Name == "ROM_Зона":
				rom_zon_param_id = e.GetDefinition().Id
		provider_zoon_param2 = ParameterValueProvider(rom_zon_param_id)
		filt_str_cont = FilterStringEquals()
		rule_str = "Квартира"
		f_str_rule = FilterStringRule(provider_zoon_param2, filt_str_cont, rule_str, True)
		
#-----------------------Фильтер-----------------------------------------------------------------------		
		sum_rule = List[FilterRule]([f_are_rule,f_str_rule])
		filter2 = ElementParameterFilter(sum_rule)
		room_elements = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WherePasses(filter2)#.WherePasses(filter)

		
#-----------------------Первый словарь с групировкой ID элементов по Типу квартир-----------------------------------------------------------------------			
		d_type={} 
		for e in room_elements:
			d_type[lookp_r_typ_str(e)] = []
		for e in room_elements:
			d_type[lookp_r_typ_str(e)].append(e.Id)

#-----------------------Второй словарь с групировкой по типам квартир, каждый тип квартиры это словарь, с групировкой ID элементов по номеру квартиры--------------------------		
		d2={}
		for e in room_elements:
			d2[lookp_r_typ_str(e)] = {}
			#x+=1
		for key in d_type:
			for r in d_type[key]:
				d2[key][lookps(doc.GetElement(r),"ROM_Номер")] = []
		for key in d_type:
			for r in d_type[key]:
				d2[key][lookps(doc.GetElement(r),"ROM_Номер")].append(lookp(doc.GetElement(r),"Площадь","d")/10.764*lookp(doc.GetElement(r),"Коэффициент","d"))

#-----------------------Третий уровень словарей сумарная площадь квартиры, с групировкой по типам--------------------------					
		d3={}
		for e in room_elements:
			d3[lookp_r_typ_str(e)] = []
		for key in d_type:
			for key2 in d2[key]:
				d3[key].append(round(sum(d2[key][key2]),2))
				
#-----------------------Четвертый уровень словаря мин-макс по типам квартиры--------------------------					
		d4={}
		for e in room_elements:
			d4[lookp_r_typ_str(e)] = 0
		for key in d_type:
			d4[key] = str(min(d3[key]))+" - "+str(max(d3[key]))
#-----------------------Пятый шаг проходимся по словарю первого уровня и записываем в него значение мин-макс из словаря 4го--------------------------	
		for key in d_type:
			for r in d_type[key]:
				doc.GetElement(r).LookupParameter("АБН_Мин-Макс").Set(d4[key])
					
			
		
		test.append(x)		
		test.append(d4.items())#.items())
		#elist = [x for x in room_elements]
		#x=+len(elist)
		#test.append(rom_zon_param_id)