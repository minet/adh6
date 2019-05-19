import ApiClient from "./api/src/ApiClient";
import MemberApi from "./api/src/api/MemberApi";

const client = new ApiClient();
client.basePath = "http://localhost:8080/api";

export const MemberGateway = new MemberApi(client);
