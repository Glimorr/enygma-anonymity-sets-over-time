package docker

import (
  "encoding/json"
  "fmt"
  "os"
  "path/filepath"
  "sort"
  "testing"
)

// TestW2SevenOfflineCompose checks that the pinned generator builds a complete
// seven-member service graph when given seven names directly. This bypasses
// the CLI's 2-6 guard, but DOES NOT deploy, register, or execute any chains.
func TestW2SevenOfflineCompose(t *testing.T) {
  dir:=os.Getenv("ENYGMA_W2_COMPOSE_OUT")
  if dir=="" { t.Skip("ENYGMA_W2_COMPOSE_OUT not set") }
  p:=[]string{"a","b","c","d","e","f","g"}
  cfg:=GetDemoComposeConfig(p,false,nil,false,nil,false,false,nil)
  essential:=[]string{"private-network-hub","postgres","proofs-api","contracts"}
  for _,name:=range essential{
    if _,ok:=cfg.Services[name];!ok{t.Fatalf("missing core service %s",name)}
  }
  names:=[]string{}
  for _,part:=range p {
    for _,name:=range []string{"privacy-node-"+part,"privacy-node-"+part+"-init","kos-"+part,"relayer-"+part}{
      if _,ok:=cfg.Services[name];!ok{t.Fatalf("missing member service %s",name)}
    }
  }
  for name:=range cfg.Services{names=append(names,name)}
  sort.Strings(names)
  servicePorts:=map[string][]string{}
  for _,name:=range names {
    if len(cfg.Services[name].Ports)>0 {
      servicePorts[name]=cfg.Services[name].Ports
    }
  }
  payload:=struct {
    EvidenceType string `json:"evidence_type"`
    Participants []string `json:"participants"`
    ServiceCount int `json:"service_count"`
    Services []string `json:"services"`
    HostPorts map[string][]string `json:"host_ports"`
    Deployed bool `json:"deployed"`
    NoLiveHubState bool `json:"no_live_hub_state"`
  }{"OFFLINE_SEVEN_MEMBER_COMPOSE_STRUCTURE",p,len(names),names,servicePorts,false,true}
  if err:=os.MkdirAll(dir,0755);err!=nil{t.Fatal(err)}
  b,err:=json.MarshalIndent(payload,"","  ")
  if err!=nil{t.Fatal(err)}
  if err:=os.WriteFile(filepath.Join(dir,"seven_member_service_graph.json"),append(b,'\n'),0644);err!=nil{t.Fatal(err)}
  fmt.Printf("W2_OFFLINE_COMPOSE_SEVEN_PASS services=%d member_count=7 no_deployment=true\n",len(names))
}
