import {baseUrl} from "../env"


export class VideoAPi<T>{
    baseUrl:string=baseUrl
        
        public async UploadVideo(data:FormData,endpoint: string = 'upload-validated-video/'){
            try{
                const response = await fetch(`${this.baseUrl}/${endpoint}`,{
                method: "POST",
                body: data
                });
                return await response.json();
            }
            catch(error){
                console.error("Ошибка при выполнении запроса:", error);
                throw error; 
            }
        }      
    }

export interface Child {
    video:File;
}



export class ChildService extends VideoAPi<Child> {
  fetch(arg0: string) {
    throw new Error("Method not implemented.");
  }
}    
    

