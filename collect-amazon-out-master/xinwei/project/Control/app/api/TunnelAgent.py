import time
import traceback
import datetime
import redis
import pickle
from xinwei.project.Control.app.setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DATABASE


class TunnelAgent(object):

    def __init__(self):
        self.serve = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DATABASE)

    def getAgentConfiguration(self) -> tuple:
        """
        Get configuration of tunnel proxy

        Retunr data of dict
        """
        try:
            result = pickle.loads(self.serve.get("AgentConfiguration")) if self.serve.get("AgentConfiguration") else {}
            return True, result
        except:
            return False, None


    # def getAgentRequestFrequency(self) -> dict:
    #     """
    #     Get max request frequency of tunnel agent
    #     Retunr data of dict
    #     """
    #     try:
    #         result = pickle.loads(self.serve.get("AgentRequestFrequency"))
    #         return result
    #     except:
    #         return {}


    def getAgentInformation(self) -> tuple:
        """
        Get infromation of tunnel proxy

        Retunr data of dict
        """
        try:
            result = pickle.loads(self.serve.get("AgentInformation")) if self.serve.get("AgentInformation") else {}
            return True, result
        except:
            return False, None

    def setAgentConfiguration(self, machine_code: str, tunnel_name: str) -> tuple:
        """
        Set configuration of tunnel proxy

        Return setting result and message
        """
        totle_agent = self.getAgentInformation()[1].keys()
        if not machine_code:
            return False, "ERROR:The machine code cannot be empty"
        if not totle_agent:
            return False, "ERROR:Failed to obtain proxy information Procedure"
        if tunnel_name not in totle_agent:
            return False, f"ERROR:<{tunnel_name}>--Agent does not exist"
        agent_configuration = self.getAgentConfiguration()[1]
        if agent_configuration is None:
            return False, "ERROR:Failed to obtain the proxy configuration data Procedure"
        agent_configuration[machine_code] = tunnel_name
        try:
            self.serve.set("AgentConfiguration", pickle.dumps(agent_configuration))
        except:
            return False, traceback.format_exc()
        return True, "Successful"

    # def setAgentRequestFrequency(self, tunnel_name: str, frequency: int) -> tuple:
    #     """
    #     Set max request frequency of tunnel agent
    #     Return setting result and message
    #     """
    #     totle_agent = self.getAgentInformation().values()
    #     if not totle_agent:
    #         return False, "设置失败，获取代理信息失败"
    #     if tunnel_name not in totle_agent:
    #         return False, f"设置失败，{tunnel_name}--代理不存在"
    #     agent_request_frequency = self.getAgentRequestFrequency()
    #     if not agent_request_frequency:
    #         return False, "设置失败，获取代理使用频率失败"
    #     if agent_request_frequency[tunnel_name] == frequency:
    #         return False, "设置失败，设置内容与原数据相同"
    #     agent_request_frequency[tunnel_name] = frequency
    #     try:
    #         self.serve.set("AgentRequestFrequency", pickle.dumps(agent_request_frequency))
    #     except:
    #         return False, traceback.format_exc()
    #     return True, "设置成功"


    def setAgentInformation(self, tunnel_name=None, address=None, user_name=None, password=None, request_frequency=None) -> tuple:
        """
        Set infromation of tunnel agent

        Return setting result and message
        """
        if not tunnel_name:
            return False, "ERROR:The tunnel name cannot be empty"
        agent_information = self.getAgentInformation()[1]
        if not address:
            try:
                address = agent_information.get(tunnel_name).get("address")
            except AttributeError:
                address = ""
        if not user_name:
            try:
                user_name = agent_information.get(tunnel_name).get("user_name")
            except AttributeError:
                user_name = ""
        if not password:
            try:
                password = agent_information.get(tunnel_name).get("password")
            except AttributeError:
                password = ""
        if not request_frequency:
            try:
                request_frequency = agent_information.get(tunnel_name).get("request_frequency")
            except AttributeError:
                request_frequency = 0
        if agent_information is None:
            return False, "ERROR:Failed to obtain information of proxy"
        agent_information[tunnel_name] = {"address": address, "user_name": user_name, "password": password, "request_frequency": request_frequency}
        try:
            self.serve.set("AgentInformation", pickle.dumps(agent_information))
        except:
            return False, traceback.format_exc()
        return True, "Successful"

    def deleteConfiguration(self, machine_code=None) -> tuple:
        """
        Delete tunnel agent configuration

        Return setting result and message
        """
        if machine_code is None:
            return False, "ERROR:The machine code cannot be empty"
        agent_configuration = self.getAgentConfiguration()[1]
        if agent_configuration is None:
            return False, "ERROR:Failed to obtain information of proxy"
        elif agent_configuration == {}:
            return False, "ERROR:The configuration data of proxy is empty"
        if machine_code not in agent_configuration.keys():
            return False, f"ERROR:<{machine_code}>--The machine code does not exist"
        agent_configuration.pop(machine_code)
        try:
            self.serve.set("AgentConfiguration", pickle.dumps(agent_configuration))
        except:
            return False, traceback.format_exc()
        return True, "Successful"

    def deleteInformation(self, tunnle_name=None) -> tuple:
        """
        Delete tunnel agent information

        Return setting result and message
        """
        if tunnle_name is None:
            return False, "ERROR:Tunnel name cannot be empty"
        agent_information = self.getAgentInformation()[1]
        if agent_information is None:
            return False, "ERROR:Failed to obtain information of tunnel proxy"
        elif agent_information == {}:
            return False, "ERROR:Proxy information is empty"
        if tunnle_name not in agent_information.keys():
            return False, f"ERROR:{tunnle_name}--The proxy does not exist"
        agent_information.pop(tunnle_name)
        try:
            self.serve.delete(tunnle_name)
            self.serve.set("AgentInformation", pickle.dumps(agent_information))

        except:
            return False, traceback.format_exc()
        return True, "Successful"

    def updateRegular(self) -> None:
        """
        Update total of token regular
        """
        self.updateAll()
        while True:
            now_time = datetime.datetime.now()
            if now_time.second == 0:
                self.updateAll()
            time.sleep(1)

    def updateAll(self) -> None:
        """
        Update max number of token according to tunnel agent setting
        """
        agent_information = self.getAgentInformation()[1]
        for tunnel in agent_information.keys():
            frequency = int(agent_information.get(tunnel).get("request_frequency"))
            left_token = self.serve.llen(tunnel)
            if left_token < frequency:
                self.serve.rpush(tunnel, *list(range(left_token, frequency)))
            elif left_token > frequency:
                self.serve.ltrim(tunnel, 0, frequency - 1)


    def getToken(self, tunnel_name=None) -> tuple:
        """
        Return token code according to tunnel name
        """
        if tunnel_name is None:
            return False, "Tunnel agent name is null"
        length = self.serve.llen(tunnel_name)
        if length == 0:
            return False, "Overclocking"
        else:
            try:
                token = int(self.serve.rpop(tunnel_name))
            except TypeError:
                return False, "Redis connect error"
            return True, token + 1

    def getEdition(self) -> tuple:
        """
        Return current edition
        """
        try:
            current_edition = float(pickle.loads(self.serve.get("CurrentEdition")))
            return True, current_edition
        except:
            return False, "???"

    def setEdition(self, edition=None) -> tuple:
        """
        Set current edition
        """
        if edition is None:
            return False, "Edition cannot be empty"
        self.serve.set("CurrentEdition", pickle.dumps(edition))
        return True, f"Successful:The latest edition:{edition}"

    def updateEdition(self) -> tuple:
        """
        Update current edition
        """
        try:
            current_edition = float(self.getEdition()[1])
            new_edition = (int(current_edition * 100 + 0.5) + 1)/100
            self.serve.set("CurrentEdition", pickle.dumps(new_edition))
            return True, f"Sucessful:The latest edition:{new_edition}"
        except:
            return False, "Failure"


if __name__ == '__main__':
    ac = TunnelAgent().getEdition()
    print(ac)
