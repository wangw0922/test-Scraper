import sys

sys.path.append('....')
import os
import execjs
import random
import re
import datetime
import time
import copy
import json
import uuid
from parsel import Selector
from lxml import etree
from hashlib import md5
from xinwei.project.Collect.src.loggerDefine import logger_define
from xinwei.project.setting import machine_mark_code
from xinwei.project.Collect.src.get_response import get_response
from xinwei.project.RedisSaveToMongoDb.src.async_save_data import AsyncMongoData
logging = logger_define(os.getcwd(), 'async_detail_parser')


class DetailParse:
    """
    Parse page of product detail
    """

    def __init__(self, url: str, response=None, task_data=None,
                 user_id=None,
                 task_id=None, primary_key=True, remark="", exception_type=0):
        # 任务数据
        if not task_data:
            self.task_data = {}
        else:
            self.task_data = task_data
        # 主体下的所有变体
        self.asins_list = []
        # 采集优先级
        if self.task_data:
            self.orderby = task_data.get("orderby")
        else:
            self.orderby = None
        # 异常类型
        self.exception_type = exception_type
        # 备注
        self.remark = remark
        # 详情页响应
        self.response = response
        # 详情
        self.data = {'isTort': False, 'available': True}
        # 概要
        self.profile = {'isCollect': True, 'status': 1}
        self.data_to_return = {}
        if self.response:
            # 选择器对象
            self.sel = Selector(response)
            # 详情页数据
            self.html = etree.HTML(response)
            # 获取dataToReturn
            self.get_data_to_return()
        # 产品链接
        self.url = url
        # 任务id
        self.task_id = task_id
        # 用户id
        self.user_id = user_id
        # asin
        self.asin = re.search('/dp/([A-Za-z\d]+)', self.url).group(1)
        # 平台
        self.platform = 1
        # 加购信息
        self.add_cart_info = ""
        # 产品状态
        self.status = 1
        # 创建时间
        self.create_time = datetime.datetime.now()
        # uuid
        self.parent_uuid = time.time()
        # 产品分类
        self.catalog = []
        # 是否刊登
        self.published = False
        # 是否包含品牌
        self.containBrand = False
        # 品牌识别是否正确
        self.branDiscernRight = False
        # 是否主键
        self.primary_key = primary_key

    @staticmethod
    def get_token(word) -> str:
        """
        Generate id（mongodb）
        """
        deomo_val = word
        md5_val = md5(deomo_val.encode('utf8')).hexdigest()
        return md5_val

    def get_data_to_return(self):
        if self.html:
            # 使用XPath定位到包含"dataToReturn"的<script>标签
            script_tag = self.html.xpath("//script[contains(text(), 'twister-js-init-dpx-data')]")
            # 检查是否找到了<script>标签
            if script_tag:
                script_text = script_tag[0].text.replace('twister-js-init-dpx-data', 'twister_js_init_dpx_data')
                snippet1 = """
                var P = {
                    register: function(name, fn) {
                        // Store the callback function
                        this[name] = fn;
                    },
                    when: function(condition) {
                        // Mock implementation for when, you can customize if needed
                        var callbacks = {};
                        return {
                            register: function(name, fn) {
                                callbacks[name] = fn;
                            }
                        };
                    }
                };
                """

                try:
                    # 使用PyExecJS执行JavaScript代码
                    ctx = execjs.compile(snippet1 + script_text)
                    # 获取 dataToReturn 的值
                    self.data_to_return = ctx.eval('P.twister_js_init_dpx_data()')

                except json.JSONDecodeError as e:
                    logging.info("data_to_return JSON解析错误:", e)
            else:
                logging.info("未找到包含dataToReturn变量的<script>标签")

    def get_isvariant(self) -> bool:
        """
        Determine whether it is variant

        Default:false
        """
        try:
            isvariant_str = re.search('"variationValues"\s:\s(\{.+?}),', self.response).group(1)
            isvariant_json = json.loads(isvariant_str)
            for each in isvariant_json.values():
                if len(each) > 1:
                    return True
            return False
        except:
            return False

    def get_dimension_values_display_data(self) -> list:
        """
        Get dimensionValuesDisplayData
        """
        try:
            isvariant_value_str = re.search('"dimensionValuesDisplayData"\s:\s(\{.+?}),', self.response).group(1)
            isvariant_value_json = json.loads(isvariant_value_str)
        except:
            return []
        return isvariant_value_json

    def get_variant_attribute(self, asin) -> list:
        """
        Get attribute and value of variant
        """
        isvariant_attr_json = {}
        isvariant_value_json = {}
        dimensions_json = []
        variant_list = []
        if self.data_to_return:
            try:
                isvariant_attr_json = self.data_to_return.get('variationDisplayLabels')
                isvariant_value_json = self.data_to_return.get('dimensionValuesDisplayData')[asin]
                dimensions_json = self.data_to_return.get('dimensions')
            except:
                pass
        else:
            try:
                isvariant_attr_str = re.search('"variationDisplayLabels"\s:\s(\{.+?}),', self.response).group(1)
                isvariant_attr_json = json.loads(isvariant_attr_str)
                isvariant_value_str = re.search('"dimensionValuesDisplayData"\s:\s(\{.+?}),', self.response).group(1)
                isvariant_value_json = json.loads(isvariant_value_str)[asin]
                dimensions_str = re.search('"dimensions"\s:\s(\[.+?]),', self.response).group(1)
                dimensions_json = json.loads(dimensions_str)
            except:
                logging.info('属性正则解析失败!')

        try:
            attr_list = [isvariant_attr_json[i] for i in dimensions_json]
            for num in range(len(attr_list)):
                variant_dict = {'name': attr_list[num], 'value': isvariant_value_json[num]}
                variant_list.append(variant_dict)
        except:
            logging.info('属性解析失败!')
        return variant_list

    def get_son_variant(self) -> list:
        """
        Get variant information
        """
        try:
            variant_json_str = re.search("jQuery\.parseJSON\('(.+?)'\);", self.response).group(1).strip()
        except:
            return []
        try:
            variant_json = json.loads(variant_json_str.replace("\\'", "'"))
            is_variant = list(self.data_to_return['dimensionValuesDisplayData'].values())
            if isinstance(is_variant, list):
                is_variant_one_str = is_variant[0][0]
            else:
                is_variant_one_str = None
            if is_variant_one_str in variant_json['colorImages']:
                son_list = {k: v for k, v in self.data_to_return['dimensionValuesDisplayData'].items() if k != self.data['asin']}
            elif ' '.join(is_variant[0]).replace('"', '\\"') in variant_json['colorImages']:
                son_list = {k: ' '.join(v).replace('"', '\\"') for k, v in self.data_to_return['dimensionValuesDisplayData'].items() if k != self.data['asin']}
            else:
                son_list = [{'type': types, 'asin': asin['asin']} for types, asin in variant_json['colorToAsin'].items()
                            if asin['asin'] != self.data['asin']]

        except:
            try:
                variant_json = json.loads(variant_json_str.replace('\\', ''))
                son_list = [{'type': types, 'asin': asin['asin']} for types, asin in variant_json['colorToAsin'].items() if
                            asin['asin'] != self.data['asin']]
            except:
                return []
        result_list = []
        if isinstance(son_list, list):
            son_list = {each['asin']: each['type'] for each in son_list}
        for asin, types in son_list.items():
            if isinstance(types, list):
                image_type = types[0]
            else:
                image_type = types
            if image_type in variant_json['colorImages'].keys():
                type_name = image_type
            elif ' '.join(types) in variant_json['colorImages'].keys():
                type_name = ' '.join(types)
            else:
                type_name = None
                logging.info(f'子变体图片解析失败! asin:{asin} types:{types} colorImages:{variant_json["colorImages"].keys()}')
            try:
                image = variant_json['colorImages'][type_name][0]['hiRes']
                images = [{"originImageUrl": each['hiRes']} for each in variant_json['colorImages'][type_name]]
            except:
                try:
                    image = variant_json['colorImages'][type_name][0]['large']
                    images = [{"originImageUrl": each['large']} for each in variant_json['colorImages'][type_name]]
                except:
                    image = None
                    images = None
            son_data = copy.deepcopy(self.data)
            son_profile = copy.deepcopy(self.profile)
            new_url = son_data['link'].replace(son_data['asin'], asin)
            if self.exception_type == -1:
                son_data['_id'] = self.get_token(
                    asin + str(self.task_id) + str(time.time()) + str(random.random()))
                son_profile['_id'] = self.get_token(
                    asin + str(self.task_id) + str(time.time()) + str(random.random()))
            else:
                son_data['_id'] = self.get_token(asin + str(self.task_id))
                son_profile['_id'] = self.get_token(asin + str(self.task_id))
            # mainImage  otherImages  description variantAttribute
            son_data['link'] = new_url
            son_data['primaryKey'] = False
            son_data['asin'] = asin
            son_data['finalPurchasePrice'] = None
            son_data['mainImage'] = {'originImageUrl': image}
            son_data['otherImages'] = images
            son_data['variantAttribute'] = self.get_variant_attribute(son_data['asin'])
            son_profile['primaryKey'] = False
            son_profile['asin'] = son_data['asin']
            if son_profile['asin'] != self.data['asin']:
                result_list.append({
                    'data': son_data,
                    'profile': son_profile
                })
        return result_list

    def get_second_brand(self):
        """
        Get second brand of product
        """
        try:
            second_brand = re.search("Visit the(.+)Store", self.response).group(1).strip()
        except:
            second_brand = ""
        return second_brand

    def get_add_cart_info(self):
        """
        Get add cart info of product
        """
        add_cart_info = ""
        xpath_str_list = ['//*[@id="gestalt_feature_div"]/div[1]/span/text()',
                          '//*[@id="gestalt_feature_div"]/div[2]/span/text()',
                          '//*[@id="gestalt-popover-button-announce"]/text()',
                          '//*[@id="rcx-subscribe-submit-button-announce"/text()]',
                          '//*[@id="rcx-subscribe-submit-button-announce"]/text()']
        for xpath_str in xpath_str_list:
            try:
                info = self.sel.xpath(xpath_str).get().strip() + " "
                if info:
                    add_cart_info += info
            except:
                continue
        return add_cart_info

    def get_changed_asin(self):
        try:
            asin = re.search('asin: "(.+?)"', self.response).group(1).strip()
            return asin
        except:
            return None

    def get_catalog(self) -> None:
        """
        Get category of product
        """
        try:
            type_list = self.sel.css('#wayfinding-breadcrumbs_feature_div > ul > li')
            for each_type in type_list:
                if each_type.css('span.a-list-item > a::text').get():
                    self.catalog.append(each_type.css('span.a-list-item > a::text').get().strip())
            if self.catalog[0] == 'Back to results':
                logging.error('---------------------Back to results----------------------------')
                for i in range(3):
                    res = get_response(self.url, task_data=self.task_data)
                    sel = Selector(res.text)
                    type_list = sel.css('#wayfinding-breadcrumbs_feature_div > ul > li')
                    for each_type in type_list:
                        if each_type.css('span.a-list-item > a::text').get():
                            self.catalog.append(each_type.css('span.a-list-item > a::text').get().strip())
                    if self.catalog[0] == 'Back to results':
                        logging.error('---------------------Back to results----------------------------')
                        logging.error(self.url)
                        time.sleep(5)
                        continue
                    else:
                        break
            if self.catalog[0] == 'Back to results':
                self.catalog = None
        except ZeroDivisionError:
            raise ZeroDivisionError("Exit...")
        except Exception:
            self.catalog = None

    def get_title(self) -> str:
        """
        Get title of protuct
        """
        try:
            title = self.sel.css('#productTitle::text').get().strip()
        except:
            title = ""
        if re.findall("[\u4e00-\u9fa5]", title):
            self.profile['isCollect'] = False
            self.remark = "标题为中文"
            self.exception_type = 17
            return ""
        return title

    def get_description(self) -> str:
        """
        Get description of product
        """
        description = ''
        description_list = self.sel.css('#productDescription > p > span')
        for each in description_list:
            description += each.get().replace('<br>', '').replace('span', '').replace('/', '').replace(
                'class="a-text-bold"', '').replace('>', '').replace('<', '')
        return description

    def get_brand(self) -> str:
        """
        Get brand of product
        """
        brand_str = self.sel.css('#productOverview_feature_div').get()
        try:
            brand = re.search('>(.+)', re.search('Brand(.+?)class="(.+?)">(.+?)</span>', brand_str).group(3)).group(
                1).strip()
        except:
            brand = None
        if brand is None:
            try:
                brand = re.search('>Manufacturer([\s\W]*?)</span>\s<span>(.+?)</span>', self.response).group(2).strip()
            except:
                brand = None
        if brand is None:
            try:
                brand_str = self.sel.css('#prodDetails').get()
                brand = re.search('Brand(.+?)">(.+?)</td>', brand_str).group(2).strip()
                if not brand:
                    brand = re.search('Manufacturer(.+?)">(.+?)</td>', brand_str).group(2).strip()
            except:
                brand = None
        if brand is None:
            try:
                brand_str = self.sel.css('#bylineInfo::text').get()
                brand = brand_str.replace('Visit the', '').replace('visit the', '').replace('Store', '').replace(
                    'store', '').replace('brand:', '').replace('Brand:', '').strip()
            except:
                brand = None
        return brand

    def get_weight(self) -> dict:
        """
        Get weight of product
        """
        weight_list = self.sel.css('#productDetails_detailBullets_sections1')
        if weight_list is None:
            weight_list = self.sel.css('product-specification-table').get()
        if weight_list is None:
            weight_list = self.sel.css('product-specification-table').get()
        weight = None
        for each_weight in weight_list:
            if each_weight.css('th::text').get() == ' Item Weight ':
                weight = each_weight.css('td::text').get()
        if not weight:
            weight_str = self.sel.css('#productDetails_techSpec_section_1').get()
            try:
                weight = re.search('Item\sWeight([\s\S]*?)">\s(.+?)</td>', weight_str).group(2).strip().replace(
                    '\u200e',
                    '')
            except:
                weight = None
        if weight is None:
            weight_str = self.sel.css('#productOverview_feature_div').get()
            try:
                weight = re.search('Item\sWeight</span>([\s\S]*?)">\s(.+?)</span>\s</td>', weight_str).group(
                    2).strip().replace('\u200e', '')
            except:
                weight = None
        if weight is None:
            weight_str = self.sel.css('#prodDetails').get()
            try:
                weight = re.search('Item\sWeight(.+?)">(.+?)</td> ', weight_str).group(2).strip()
            except:
                weight = None
        if weight:
            try:
                amount = re.search('\d+?\.*?\d*?', weight).group()
                unit = re.search('\w+?', weight).group()
                result = {'amount': int(amount.strip()), 'unit': unit}
            except:
                result = None
        else:
            result = None
        return result

    def get_final_purchase_price(self) -> float:
        """
        Get price of product
        """
        price_str = self.sel.css('#corePrice_feature_div > div > span > span.a-offscreen::text').get()
        try:
            price = float(re.search('\d+?\.\d*', price_str).group())
        except:
            price = None
        if price is None:
            try:
                price = float(re.search('class="a-offscreen">(.+?)<', self.response).group(1)[1:])
            except:
                price = None
        return price

    def get_comment_count(self) -> int:
        """
        Get product comment count
        """
        try:
            evaluate_str = self.sel.css('#acrCustomerReviewText::text').get().replace(',', '').replace(' ', '')
            evaluate = int(re.search('\d+', evaluate_str).group())
        except:
            evaluate = 0
        return evaluate

    def get_grade(self) -> float:
        """
        Obtain product score
        """
        rank_str = self.sel.css('#acrPopover > span.a-declarative > a > i > span::text').get()
        try:
            rank = float(re.search('\d\.\d', rank_str).group())
        except:
            rank = 0
        return rank

    def get_main_image(self) -> dict:
        """
        Obtain main picture of product
        """
        try:
            images_str = re.search("'colorImages': {(.+?)}]}", self.response).group(1)
            image_list = re.findall('"hiRes":"(.+?jpg)"', images_str)
            if not image_list:
                image_list = re.findall('"large":"(.+?jpg)"', images_str)
            if image_list:
                main_image = image_list[0]
                if 'http' in main_image:
                    result = main_image
                    return {'originImageUrl': result}
                else:
                    return {}
            else:
                return {}
        except:
            result = None
        if result:
            return {'originImageUrl': result}
        else:
            return {}

    def get_other_images(self) -> list:
        """
        Obtain other picture of product
        """
        try:
            images_str = re.search("'colorImages': {(.+?)}]}", self.response).group(1)
            image_list = re.findall('"hiRes":"(.+?jpg)"', images_str)
            other_image = image_list[1:]
        except:
            other_image = None
        if other_image:
            other_image_list = [{'originImageUrl': each_other} for each_other in other_image]
            return other_image_list
        else:
            return [self.get_main_image()]

    def get_product_size(self) -> dict:
        """
        Obtain size of product
        """
        try:
            size_str = re.search('Product\sDimensions([\s\S]+?)</li>',
                                 self.response).group(1).strip()
            size = re.search('>\s*?(\d+?\.*?\d*?\sx\s\d+?\.*?\d*?\sx\s\d+?\.*?\d*)\s(\w+)', size_str).group(1)
            unit = re.search('>\s*?(\d+?\.*?\d*?\sx\s\d+?\.*?\d*?\sx\s\d+?\.*?\d*)\s(\w+)', size_str).group(2)
            try:
                length, wide, high = [each.strip() for each in size.split('x')]
                size_dict = {
                    'length': {'amount': int(length.replace('\u200e', '').strip()), 'unit': unit},
                    'wide': {'amount': int(wide.strip()), 'unit': unit},
                    'high': {'amount': int(high.strip()), 'unit': unit}
                }
            except:
                size_dict = None
        except:
            size_dict = None
        return size_dict

    def get_one_catalog(self) -> str:
        """
        Obtain first level category of product
        """
        if self.catalog:
            if re.findall("[\u4e00-\u9fa5]", self.catalog[0]):
                self.profile['isCollect'] = False
                self.remark = "分类为中文"
                self.exception_type = 17
                return ""
            return self.catalog[0]
        else:
            return ""

    def get_package_size(self) -> dict:
        """
        Obtain package size of product
        """
        size_str = self.sel.css('#productDetails_techSpec_section_1').get()
        if size_str is None:
            size_str = self.sel.css('product-specification-table').get()
        try:
            size = re.search('Item\sDimensions\sLxWxH([\s\S]*?)">\s(.+?)inches', size_str).group(2).strip()
            try:
                length, wide, high = [each.strip() for each in size.split('x')]
                size_dict = {
                    'length': int(length.replace('\u200e', '').strip()),
                    'wide': int(wide.strip()),
                    'high': int(high.strip())
                }
            except:
                size_dict = size
        except:
            size_dict = None
        if size_dict is None:
            try:
                size = re.search(
                    'Item\sDimensions\sLxWxH([\s\S]*?)">\s(\d+?\.*?\d+?\sx\s\d+?\.*?\d+?\sx\s\d+?\.*?\d+)\sinches',
                    self.response).group(2).strip()
                try:
                    length, wide, high = [each.strip() for each in size.split('x')]
                    size_dict = {
                        'length': length.replace('\u200e', ''),
                        'wide': wide,
                        'high': high
                    }
                except:
                    size_dict = size
            except:
                size_dict = None
        return size_dict

    def get_features(self) -> list:
        """
        Obtain features of product
        """
        features = []
        features_list = self.sel.css('#feature-bullets > ul > li')
        if not features_list:
            features_list = self.sel.css('#pov2FeatureBulletsExpanderContent > ul > li')
        if not features_list:
            features_list = self.html.xpath('//*[@id="productFactsDesktopExpander"]/div[1]/ul')
            for each_features in features_list:
                attribute = each_features.xpath('./span/li/span/text()')[0].strip()
                if attribute:
                    features.append(attribute)
        else:
            for each_features in features_list:
                attribute = each_features.css('span.a-list-item::text').get().strip()
                if attribute:
                    features.append(attribute)
        return features

    def get_produce_country(self) -> str:
        """
        Obtain place of origin
        """
        country_str = self.sel.css('#productDetails_techSpec_section_1').get()
        if country_str is None:
            country_str = self.sel.css('product-specification-table').get()
        if country_str is None:
            country_str = self.sel.css('#prodDetails').get()
        try:
            country = re.search('Country\sof\sOrigin([\s\S]*?)">(.+?)</td>', country_str).group(2).strip()
        except:
            country = None
        return country

    def get_parents_uuid(self, parents_uuid=None) -> str:
        """
        Get uuid
        """
        if self.data['isVariant']:
            parents_uuid = str(uuid.uuid4())
        return parents_uuid

    @staticmethod
    def in_tort(key, keys) -> bool:
        """
        Determine whether tort
        """
        if re.findall(f'[-_]{key}[-_]', keys, re.IGNORECASE) \
                or re.findall(f'^{key}[-_]', keys, re.IGNORECASE) \
                or re.findall(f'[-_]{key}$', keys, re.IGNORECASE) \
                or re.findall(f'\s{key}\s', keys, re.IGNORECASE) \
                or re.findall(f'^{key}\s', keys, re.IGNORECASE) \
                or re.findall(f'\s{key}$', keys, re.IGNORECASE) \
                or re.findall(f'\s{key}[-_]', keys, re.IGNORECASE) \
                or re.findall(f'[-_]{key}\s', keys, re.IGNORECASE) \
                or re.findall(f"{key}'s", keys, re.IGNORECASE):
            return True
        else:
            return False

    def screen(self) -> int:
        """
        Filter data

        Return exception type
        """
        if self.exception_type == 0:
            # 筛选价格
            if self.data['finalPurchasePrice'] and self.data['finalPurchasePrice'] <= 3:
                self.remark = f'商品价格不达标：{self.data["finalPurchasePrice"]}'
                self.profile['isCollect'] = False
                return 20
            # 筛选主图
            if not self.data['mainImage']:
                self.remark = '商品主图异常'
                self.profile['isCollect'] = False
                self.data['available'] = False
                return 14
            # 筛选标题
            if not self.data['title']:
                self.remark = '商品标题异常'
                self.profile['isCollect'] = False
                return 6
            # 筛选评分
            if self.data['grade'] and 0 < self.data['grade'] < 3:
                self.remark = f'商品评分不达标:{self.data["grade"]}'
                self.profile['isCollect'] = False
                return 3
            # 筛选描述
            # if self.task_data.get('key_tort') and self.data['description']:
            #     try:
            #         keys = self.sel.css('#buybox').get()
            #         for each_key in self.task_data.get('key_tort').keys():
            #             if self.in_tort(each_key, self.data['description']) or (keys and self.in_tort(each_key, keys)):
            #                 self.remark = f'关键字侵权，侵权字段为：{each_key}'
            #                 self.data['isTort'] = True
            #                 self.data['available'] = False
            #                 tormsg = {'type': 4, 'value': each_key}
            #                 self.data['tortMsg'] = tormsg
            #                 if self.task_data.get('key_tort')[each_key] is False:
            #                     self.profile['isCollect'] = False
            #                 return 12
            #     except:
            #         self.remark = ''
            # # 筛选分类
            # if self.task_data.get('catalog_tort') and self.catalog:
            #     try:
            #         for each_catalog in self.task_data.get('catalog_tort'):
            #             if each_catalog in self.catalog:
            #                 self.remark = f'商品分类侵权，侵权字段为：{each_catalog}'
            #                 self.data['isTort'] = True
            #                 self.data['available'] = False
            #                 tormsg = {'type': 5, 'value': each_catalog}
            #                 self.data['tortMsg'] = tormsg
            #                 if self.task_data.get('catalog_tort')[each_catalog] is False:
            #                     self.profile['isCollect'] = False
            #                 return 11
            #     except:
            #         self.remark = ''
            # 筛选品牌
            # if self.task_data.get('brand_tort') and self.data['brand']:
            #     try:
            #         for each_brand in self.task_data.get('brand_tort'):
            #             if each_brand == self.data['brand'] or self.in_tort(each_brand, self.data['title']):
            #                 self.remark = f'品牌侵权，侵权字段为：{each_brand}'
            #                 self.data['isTort'] = True
            #                 self.data['available'] = False
            #                 tormsg = {'type': 1, 'value': each_brand}
            #                 self.data['tortMsg'] = tormsg
            #                 if self.task_data.get('brand_tort')[each_brand] is False:
            #                     self.profile['isCollect'] = False
            #                 return 9
            #     except:
            #         self.remark = ''
            # 筛选标题侵权
            # if self.data['title'] and self.task_data.get('title_tort'):
            #     try:
            #         for each_title in self.task_data.get('title_tort'):
            #             if self.in_tort(each_title, self.data['title']):
            #                 self.remark = f"标题侵权，侵权字段为：{each_title}"
            #                 self.data['isTort'] = True
            #                 self.data['available'] = False
            #                 tormsg = {'type': 2, 'value': each_title}
            #                 self.data['tortMsg'] = tormsg
            #                 if self.task_data.get('title_tort')[each_title] is False:
            #                     self.profile['isCollect'] = False
            #                 return 7
            #     except:
            #         self.remark = ''
            # 筛选变体数据
            if self.get_isvariant() and not self.get_son_variant():
                self.remark = '变体数据异常'
                return 13
            # 筛选价格异常
            if not self.data['finalPurchasePrice']:
                self.remark = '商品价格异常'
                return 16
            # 筛选分类异常
            if not self.catalog:
                self.remark = '商品分类异常'
                return 10
            # 筛选品牌异常
            if not self.data['brand']:
                self.remark = '商品品牌异常'
                return 8
            # 筛选评论数
            if self.data['commentCount'] and 0 < self.data['commentCount'] < 100:
                self.remark = f'商品评论数不达标:{self.data["commentCount"]}'
                return 5
            # 筛选评论数异常
            if not self.data['commentCount']:
                return 4
            # 筛选评分异常
            if not self.data['grade']:
                return 2
            # 筛选特征（卖点）异常
            if not self.data['features']:
                return 1
            return 0
        # asin集合任务跳过筛选
        elif self.exception_type == -1:
            return 0
        # 列表页已筛选，直接返回
        else:
            return self.exception_type

    def get_data(self) -> None:
        """
        Generate detail data
        """
        if self.response:
            if self.exception_type == -1:
                self.data['_id'] = self.get_token(
                    self.asin + str(self.task_id) + str(time.time()) + str(random.random()))
                self.data["taskType"] = 2
            else:
                self.data['_id'] = self.get_token(self.asin + str(self.task_id))
                self.data["taskType"] = 1
            self.data['isVariant'] = self.get_isvariant()
            self.data['platform'] = self.platform
            self.data['asin'] = self.asin
            changed_asin = self.get_changed_asin()
            self.data['changed_asin'] = changed_asin if changed_asin != self.asin else ""
            self.data['link'] = self.url
            self.get_catalog()
            self.data['catalog'] = self.catalog
            self.data['title'] = self.get_title()
            self.data['description'] = self.get_description()
            self.data['brand'] = self.get_brand()
            self.data['weight'] = self.get_weight()
            self.data['finalPurchasePrice'] = self.get_final_purchase_price()
            self.data['status'] = self.status
            self.data['commentCount'] = self.get_comment_count()
            self.data['grade'] = self.get_grade()
            self.data['createTime'] = self.create_time
            self.data['srcCreateTime'] = self.create_time
            self.data['mainImage'] = self.get_main_image()
            self.data["add_cart_info"] = self.get_add_cart_info()
            self.data["second_brand"] = self.get_second_brand()
            self.data['otherImages'] = self.get_other_images()
            self.data['primaryKey'] = self.primary_key
            self.data['parentUuid'] = self.get_parents_uuid()
            self.data['oneCatalog'] = self.get_one_catalog()
            self.data['features'] = self.get_features()
            self.data['containBrand'] = self.containBrand
            self.data['variantAttribute'] = self.get_variant_attribute(self.asin)
            self.data['produceCountry'] = self.get_produce_country()
            self.data['recordId'] = 0
            self.data['userId'] = self.user_id
            self.data['taskId'] = self.task_id
            self.data['class'] = 'com.xinwei.common.mongo.mo.CollectAmazonProductMO'
            self.data['mainImageIsOcr'] = False
            self.data['machine_mark_code'] = machine_mark_code
            self.data['orderby'] = self.orderby if self.orderby else 0
        else:
            self.profile['isCollect'] = False
            self.exception_type = 17
            if self.remark == "" or self.remark is None:
                self.remark = "详情页面响应为空"

    def get_profile(self) -> None:
        """
        Generate profile data
        """
        if self.exception_type == -1:
            self.profile['_id'] = self.get_token(
                self.asin + str(self.task_id) + str(time.time()) + str(random.random()))
        else:
            self.profile['_id'] = self.get_token(self.asin + str(self.task_id))
        self.profile['type'] = 2
        self.profile['primaryKey'] = self.primary_key
        if self.data:
            self.profile['isVariant'] = self.data.get('isVariant')
            self.profile['parentUuid'] = self.data.get('parentUuid')
        else:
            self.profile['isVariant'] = None
            self.profile['parentUuid'] = None
        self.profile['asin'] = self.asin
        self.profile['link'] = self.url
        self.profile['userId'] = self.user_id
        self.profile['taskId'] = self.task_id
        self.profile['createTime'] = datetime.datetime.now()
        self.profile['class'] = 'com.xinwei.common.mongo.mo.CollectAmazonNoteMO'
        self.profile['exceptionType'] = self.screen()
        self.profile['remark'] = self.remark
        self.profile['machine_mark_code'] = machine_mark_code

    def get_asins_list(self):
        """
        Get asins
        """
        dimension_values_display_dat = self.get_dimension_values_display_data()
        self.asins_list = dimension_values_display_dat

    def run_parse(self) -> list:
        """
        Generate list of data
        """
        self.get_data()
        self.get_profile()
        # self.get_asins_list()
        if not self.profile['isCollect']:
            self.profile['status'] = -1
            # self.data = None
            # return [{
            #     'data': self.data,
            #     'profile': self.profile
            # }]
        else:
            self.profile['status'] = 1
            # if self.exception_type == -1:
            #     return [{
            #         'data': self.data,
            #         'profile': self.profile
            #     }]
            # if self.data.get('isVariant') and self.get_son_variant():
        son_variant = self.get_son_variant()
        if self.data.get('isVariant') and son_variant:
            data_list = [{'data': self.data, 'profile': self.profile}]
            # data_list.extend(son_variant)
            # 使用字典来去重，保留第一次出现的元素
            # unique_data = {}
            # for item in son_variant:
            #     asin = item['profile']['asin']
            #     if asin not in unique_data:
            #         unique_data[asin] = item
            # 获取去重后的列表
            # data_list = list(unique_data.keys())
            if self.task_data.get('is_first_task') == 1:  # 第一次任务
                asin_list = [i for i in self.data_to_return['dimensionValuesDisplayData'].keys() if i != self.asin]
                asins = {
                    "taskId": f'{self.task_id}',
                    "PrimitiveAsin": self.asin,
                    "asin": ','.join(list(set(asin_list)))
                }
                AsyncMongoData(data_list='').save_asins(asins)
        else:
            data_list = [{
                'data': self.data,
                'profile': self.profile
            }]
        return data_list


if __name__ == '__main__':
    _url = "https://www.amazon.com/dp/B0073X2XZW/"
    _response = get_response(_url, verify=False)
    a = DetailParse(response=_response.text, url=_url).run_parse()
    print(a)
